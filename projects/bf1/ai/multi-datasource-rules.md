# Multi-Datasource & Transaction Rules

## 1. Datasource Architecture Overview

Each project may have multiple independent datasources with HikariCP connection pools.
Each datasource has its own `EntityManagerFactory` and `TransactionManager`.

Common YAML config keys:

| YAML key | Used for |
|---|---|
| `spring.datasource.jdbc` | Spring Batch, raw JDBC tasks |
| `spring.datasource.rw` | Primary app datasource |
| `spring.datasource.<module>` | Module-specific datasource |

> **Rule:** Do not add a new datasource if the domain can belong to an existing one. Discuss with the team before creating a new datasource bean.

---

## 2. YAML Configuration

```yaml
spring:
  datasource:
    hibernate:
      show_sql: false
      dialect: org.hibernate.dialect.PostgreSQLDialect
      hbm2ddl:
        auto: update                     # production: validate, dev: update
      schema_update:
        unique_constraint_strategy: RECREATE_QUIETLY

    # --- Primary datasource ---
    rw:
      driver-class-name: org.postgresql.Driver
      url: jdbc:postgresql://${env.db.host}:${env.db.port}/<db_name>
      username: <username>
      password: <password>
      type: com.zaxxer.hikari.HikariDataSource
      hikari:
        pool-name: rw
        auto-commit: false
        minimum-idle: 1
        maximum-pool-size: 5             # prod: 25
        connection-timeout: 45000
        idle-timeout: 600000
        max-lifetime: 600000
        leak-detection-threshold: 30000

    # --- Secondary datasource (if needed) ---
    <module>:
      driver-class-name: org.postgresql.Driver
      url: jdbc:postgresql://${env.db.host}:${env.db.port}/<module_db>
      username: <username>
      password: <password>
      type: com.zaxxer.hikari.HikariDataSource
      hikari:
        pool-name: <module>
        auto-commit: false
        minimum-idle: 1
        maximum-pool-size: 5
        connection-timeout: 45000
        idle-timeout: 600000
        max-lifetime: 600000
        leak-detection-threshold: 30000
```

---

## 3. Pattern for a New Module with a Dedicated Datasource

### 3a. DataModuleConfig — declare DataSource, EMF, TransactionManager

```java
@Configuration
@ComponentScan(basePackages = {
    "<base.package.module>",
})
@Slf4j
public class XxxDataModuleConfig {

  public static final String ENTITY_MANAGER_FACTORY = "xxxEntityManagerFactory";
  public static final String TRANSACTION_MANAGER    = "xxxTransactionManager";
  public static final String DS_BEAN                = "xxxDataSource";

  // Reads config from spring.datasource.<module>
  @Bean(DS_BEAN)
  @ConfigurationProperties("spring.datasource.<module>")
  DataSource xxxDataSource() {
    return DataSourceBuilder.create().type(HikariDataSource.class).build();
  }

  @Bean(ENTITY_MANAGER_FACTORY)
  LocalContainerEntityManagerFactoryBean xxxEntityManagerFactory(
      @Value("${spring.datasource.hibernate.hbm2ddl.auto:update}") String hbm2ddlAuto,
      @Value("${spring.datasource.hibernate.dialect:org.hibernate.dialect.HSQLDialect}") String hibernateDialect,
      @Value("${spring.datasource.hibernate.show_sql:false}") String hibernateShowSql,
      @Qualifier(DS_BEAN) DataSource ds) {

    LocalContainerEntityManagerFactoryBean factoryBean = new LocalContainerEntityManagerFactoryBean();
    factoryBean.setDataSource(ds);
    factoryBean.setPackagesToScan(
        "<base.package.module>"
        // add packages containing @Entity classes here
    );
    factoryBean.setJpaVendorAdapter(new HibernateJpaVendorAdapter());

    HashMap<String, Object> jpaProps = new HashMap<>();
    jpaProps.put("hibernate.hbm2ddl.auto",                           hbm2ddlAuto);
    jpaProps.put("hibernate.dialect",                                hibernateDialect);
    jpaProps.put("hibernate.show_sql",                               hibernateShowSql);
    jpaProps.put("hibernate.format_sql",                             "true");
    jpaProps.put("hibernate.enable_lazy_load_no_trans",              "true");
    jpaProps.put("hibernate.connection.provider_disables_autocommit","true");
    jpaProps.put("hibernate.globally_quoted_identifiers",            "true");

    factoryBean.setJpaPropertyMap(jpaProps);
    log.info("Created EntityManagerFactory for {}", DS_BEAN);
    return factoryBean;
  }

  @Bean(TRANSACTION_MANAGER)
  PlatformTransactionManager xxxTransactionManager(
      @Qualifier(ENTITY_MANAGER_FACTORY) LocalContainerEntityManagerFactoryBean factory) {
    log.info("Created TransactionManager name = {}", TRANSACTION_MANAGER);
    JpaTransactionManager tm = new JpaTransactionManager();
    tm.setEntityManagerFactory(factory.getObject());
    return tm;
  }
}
```

### 3b. ServiceModuleConfig — wire repository to the correct EMF & TransactionManager

```java
@Configuration
@EnableJpaRepositories(
    basePackages = "<base.package.module>.repository",
    entityManagerFactoryRef  = XxxDataModuleConfig.ENTITY_MANAGER_FACTORY,
    transactionManagerRef    = XxxDataModuleConfig.TRANSACTION_MANAGER,
    repositoryFactoryBeanClass = DataTPRepositoryFactoryBean.class
)
@Import(XxxDataModuleConfig.class)
@EnableConfigurationProperties
@EnableTransactionManagement
public class XxxServiceModuleConfig {
}
```

> **Required:** Always declare `entityManagerFactoryRef` and `transactionManagerRef` when the module does not use the primary datasource. Missing these will cause Spring to inject the wrong TransactionManager, leading to hard-to-debug runtime errors.

---

## 4. @Transactional Rules

### 4a. Service layer — the only place to put @Transactional

```java
@Service("XxxService")
public class XxxService {

  @Autowired
  private XxxLogic xxxLogic;

  // Read operation → readOnly = true for optimization (no lock, read-only hint)
  @Transactional(readOnly = true)
  public XxxEntity getById(ClientContext ctx, Long id) {
    return xxxLogic.getById(ctx, id);
  }

  // Write operation → default transaction
  @Transactional
  public XxxEntity save(ClientContext ctx, XxxEntity entity) {
    return xxxLogic.save(ctx, entity);
  }

  // If the module uses a non-primary datasource, specify the transactionManager
  @Transactional(transactionManager = XxxDataModuleConfig.TRANSACTION_MANAGER)
  public XxxEntity saveWithCustomDs(ClientContext ctx, XxxEntity entity) {
    return xxxLogic.save(ctx, entity);
  }
}
```

### 4b. Logic layer — NO @Transactional

Logic classes (`*Logic`) contain business rules and call repositories. Do not open transactions here — let the service layer control the boundary.

```java
@Component
public class XxxLogic {

  @Autowired
  private XxxRepository repo;

  public XxxEntity save(ClientContext ctx, XxxEntity entity) {
    // validate, transform...
    return repo.save(entity);
  }
}
```

### 4c. Repository layer — NO arbitrary @Transactional

Spring Data JPA already provides default transactions for CRUD methods. Only add `@Transactional` when overriding behavior (bulk delete, modifying query).

```java
public interface XxxRepository extends JpaRepository<XxxEntity, Long> {

  @Transactional
  @Modifying
  @Query("UPDATE XxxEntity e SET e.status = :status WHERE e.id = :id")
  int updateStatus(@Param("id") Long id, @Param("status") String status);
}
```

---

## 5. Multi-Datasource Rules for Cross-Module Transactions

**Do not use distributed transactions (XA).**

If a use case needs to write to multiple datasources:
1. Split into independent service calls, each with its own transaction.
2. Handle rollback manually or use Saga/event-driven patterns for eventual consistency.
3. Do not call a `@Transactional` method of module A from inside a `@Transactional` method of module B when they use different datasources — Spring will not auto-enlist cross-datasource transactions.

---

## 6. Checklist for a New Module with a Dedicated Datasource

- [ ] Create `XxxDataModuleConfig` with 3 beans: `DataSource`, `EntityManagerFactory`, `TransactionManager`
- [ ] Expose bean name constants as `public static final String` for child modules to reference
- [ ] Declare `@EnableJpaRepositories` with both `entityManagerFactoryRef` and `transactionManagerRef`
- [ ] Use `DataTPRepositoryFactoryBean.class` for `repositoryFactoryBeanClass`
- [ ] `@Import(XxxDataModuleConfig.class)` in ServiceModuleConfig
- [ ] Service methods: `@Transactional(readOnly = true)` for reads, `@Transactional` for writes
- [ ] If module uses a non-primary datasource, specify `transactionManager` in `@Transactional`
- [ ] Add entity packages to `setPackagesToScan(...)` — missing this will prevent table creation/schema validation
- [ ] Add YAML datasource config in the app config file
- [ ] Set `hbm2ddl.auto = validate` in production

---

## 7. Common Errors

| Symptom | Cause | Fix |
|---|---|---|
| `No qualifying bean of type 'EntityManagerFactory'` | Multiple EMFs, no `@Qualifier` specified | Add `@Qualifier(XxxDataModuleConfig.ENTITY_MANAGER_FACTORY)` |
| `TransactionRequiredException` | Repository calls `@Modifying` query without `@Transactional` | Add `@Transactional` to the repository method or service |
| Data not rolled back on exception | `@Transactional` placed on a logic/private method | Move `@Transactional` to a public service method |
| `LazyInitializationException` | Accessing lazy collection outside transaction | Set `hibernate.enable_lazy_load_no_trans=true`; if still failing use `JOIN FETCH` |
| Data written to wrong database | `@EnableJpaRepositories` missing `entityManagerFactoryRef` | Add both `entityManagerFactoryRef` and `transactionManagerRef` |

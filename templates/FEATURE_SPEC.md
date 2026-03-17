# Feature: [Feature Name]

**Status:** 🟡 Draft / 🟢 Approved  
**Parent Project:** [Project Name]  
**Forgejo Issue:** #issue-id  

## 1. 🎯 Purpose (User Story)
*As a [User], I want [Action], so that [Benefit].*

## 2. 📝 Functional Requirements (What it does)
- [ ] User can click Button A to do Action B.
- [ ] System must validate Input C.
- [ ] Error message D is shown if F fails.

## 3. 🏗 Technical Design (How it works)
*Architecture, DB Schema, API endpoints.*

### Database Changes
```sql
CREATE TABLE ...
```

### API Endpoints
- `POST /api/v1/resource`: Create resource.
- `GET /api/v1/resource/:id`: Get detail.

### Edge Cases & Risks
- What if network fails?
- Performance impact?

## 4. ✅ Acceptance Criteria (Definition of Done)
- [ ] Unit tests pass.
- [ ] Code reviewed.
- [ ] Manual QA passed.

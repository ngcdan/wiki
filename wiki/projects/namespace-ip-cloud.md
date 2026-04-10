---
title: "Namespace & IP Cloud"
tags: [infrastructure, network, cloud]
---




service/crm-server    ClusterIP   10.43.190.218   <none>        22/TCP,80/TCP,5432/TCP   13d
service/document      ClusterIP   10.43.21.170    <none>        22/TCP,80/TCP,5432/TCP   85d
service/egov-server   ClusterIP   10.43.151.168   <none>        22/TCP,80/TCP,5432/TCP   74d
service/fms-server    ClusterIP   10.43.213.182   <none>        22/TCP,80/TCP,5432/TCP   10d
service/postgres      ClusterIP   10.43.208.241   <none>        5432/TCP                 72d
service/server        ClusterIP   10.43.110.251   <none>        22/TCP,80/TCP            72d
service/tms-server    ClusterIP   10.43.155.166   <none>        22/TCP,80/TCP,5432/TCP   6d21h


service/win-server-2022-bfsone         ClusterIP      10.43.89.227   <none>                        3389/TCP,1433/TCP,1434/UDP   16h
service/win-server-2022-mssql          ClusterIP      10.43.75.99    <none>                        3389/TCP,1433/TCP,1434/UDP   16h
service/win-server-2022-mssql-public   LoadBalancer   10.43.45.49    14.225.17.104,14.225.17.105   51410:31759/TCP              12h
service/win-server-bfs1-db             ClusterIP      10.43.223.69   <none>                        3389/TCP                     152d

NAME                                             READY   STATUS    RESTARTS   AGE
pod/virt-launcher-win-server-2022-bfsone-2lwjj   2/2     Running   0          16h
pod/virt-launcher-win-server-2022-mssql-dh55k    2/2     Running   0          11h
pod/virt-launcher-win-server-bfs1-db-b98rq       2/2     Running   0          32m

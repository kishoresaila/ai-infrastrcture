# Docker networking

Drivers:
- bridge (default): private network on the host; containers reach each other by IP; user-defined bridges add DNS by container name.
- host: container shares the host network stack (no port mapping needed).
- none: no networking.
- overlay: multi-host networking for Swarm.
- macvlan: gives the container its own MAC/IP on the physical LAN.

```bash
docker network ls
docker network create appnet
docker run -d --network appnet --name db postgres
docker network inspect appnet
```
Publish a port with `-p 8080:80`. In Docker Compose, services on the same compose network reach each other by service name.

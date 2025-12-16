# Zombie World War - Backend

Spring Boot 3 backend service for the Zombie World War game.

## Tech Stack

- Java 17
- Spring Boot 3.2.0
- Spring Data JPA
- Spring Security with JWT
- MySQL 8.0
- H2 (for testing)

## Prerequisites

- JDK 17+
- Maven 3.8+
- MySQL 8.0+

## Database Setup

1. Create MySQL database:
```sql
CREATE DATABASE zombie_world_war CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Run the migration script located at:
   `src/main/resources/db/migration/V1__create_initial_schema.sql`

## Configuration

Set environment variables or update `application.yml`:

```bash
export DB_USERNAME=your_username
export DB_PASSWORD=your_password
export JWT_SECRET=your-256-bit-secret-key-minimum-32-characters
```

## Running the Application

```bash
# Build
mvn clean package

# Run
mvn spring-boot:run

# Or run the JAR
java -jar target/zombie-world-war-backend-1.0.0-SNAPSHOT.jar
```

## Running Tests

```bash
# Run all tests
mvn test

# Run with coverage
mvn test jacoco:report
```

## API Endpoints

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/game/save` - Save game state
- `GET /api/game/load/{id}` - Load game state
- `GET /api/game/saves` - List user saves
- `DELETE /api/game/save/{id}` - Delete save
- `POST /api/leaderboard/submit` - Submit score
- `GET /api/leaderboard/top` - Get top scores
- `GET /api/leaderboard/rank/{userId}` - Get user rank

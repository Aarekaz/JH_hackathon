# AI Parliament Database Documentation

## Overview
The AI Parliament system uses SQLAlchemy with SQLite as its database backend. The database structure supports parliamentary debates around AI policy papers, with MPs representing different sectors providing responses and votes.

## Database Models

### 1. Debate Model
The Debate model represents a parliamentary debate session with:
- Primary key ID
- Title and description of the debate topic
- Policy text being discussed
- Status tracking ('active', 'completed', etc)
- Creation timestamp
- Foreign key relationship to PolicyPaper
- One-to-many relationships with MPResponses and Votes

### 2. MPResponse Model


## Database Operations

### Repository Pattern
The system uses a repository pattern for database operations through the DebateRepository class:

#### 1. Debate Operations
Key operations:
- Create new debates
- Retrieve debates by ID
- Update debate status

#### 2. Response Operations

Handles:
- Adding MP responses to debates
- Retrieving debate responses
- Managing response relationships

#### 3. Vote Operations
```python:backend/repositories/debate_repository.py
startLine: 70
endLine: 92
```

Manages:
- Vote creation
- Vote retrieval
- Vote tallying

### Database Initialization
Database initialization happens at application startup:
```python:backend/main.py
startLine: 12
endLine: 16
```

## Database Relationships

### One-to-One Relationships
- PolicyPaper to Debate: Each policy paper can have one active debate

### One-to-Many Relationships
- Debate to MPResponses: Each debate has multiple MP responses
- Debate to Votes: Each debate collects multiple votes

## Transaction Management

### Session Handling
Sessions are managed through FastAPI dependency injection:
```python:backend/routers/debates.py
startLine: 12
endLine: 21
```

### Error Handling
Database operations include transaction management:
```python:backend/routers/policy_papers.py
startLine: 26
endLine: 53
```

## Database Access Patterns

### Direct Access
Used in simple queries through SQLAlchemy:
```python:backend/repositories/debate_repository.py
startLine: 22
endLine: 25
```

### Repository Access
Complex operations use the repository pattern:
```python:backend/repositories/debate_repository.py
startLine: 93
endLine: 115
```

## Testing
Database operations can be tested using the test endpoints:
```python:backend/test_endpoints.py
startLine: 14
endLine: 50
```

## Best Practices
1. Always use repository pattern for database operations
2. Include proper error handling and rollbacks
3. Use async operations where possible
4. Maintain proper relationship cascades
5. Include proper indexing on frequently queried fields
6. Use transaction management for multi-step operations
7. Implement proper data validation before database operations

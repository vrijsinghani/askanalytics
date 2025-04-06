# Developer Standards and Best Practices

This document outlines the coding standards, patterns, and best practices for the AskAnalytics project.  Clean code first!  No hacking or hard coded solutions.
Always ask yourself when creating a solution, "Is this what a world class developer would do?"
## UI Component Development

### 1. HTMX-First Approach
- Use HTMX for interactive elements whenever possible
- Minimize JavaScript to essential functionality only
- Structure components to support progressive enhancement

### 2. Component Structure
- Create reusable Django template partials in `templates/components/`
- Use Django template inheritance for consistent layouts
- Document component parameters and usage examples

### 3. Styling Guidelines
- Follow BEM (Block Element Modifier) naming convention
- Use CSS variables for theming (support light/dark modes)
- Maintain responsive design principles

## Multi-tenancy Implementation

### 1. Data Access Patterns
- Always use the organization-aware model managers
- Never bypass the organization context in queries
- Use `get_queryset()` overrides that respect organization boundaries

### 2. File Access in Multi-tenant Context
- Always use SecureFileStorage for organization-specific files
- Include organization context in file paths
- Implement proper access control checks before serving files

### 3. Cross-tenant Security
- Use the security middleware to prevent tenant data leakage
- Implement explicit permission checks for all views
- Audit all API endpoints for proper tenant isolation

## Asynchronous Operations

### 1. WebSocket Standards
- Use authenticated WebSocket connections
- Implement proper error handling and reconnection logic
- Structure message formats consistently (JSON with action/payload pattern)

### 2. Celery Task Standards
- Use Celery for all long-running operations
- Include organization context in all task parameters
- Implement proper error handling and retry mechanisms
- Store task results with organization context
- Use task routing for different task types
- Implement task prioritization for critical operations

### 3. Celery Configuration and Monitoring
- Configure Celery with Redis as the broker and result backend
- Implement proper task logging with correlation IDs
- Set up monitoring for Celery workers and queues
- Configure task timeouts and rate limits appropriately
- Implement dead letter queues for failed tasks

### 4. Redis Usage Standards
- Use Redis for caching, session storage, and Celery broker
- Implement proper key namespacing with organization context
- Set appropriate TTL (time-to-live) for cached data
- Use Redis transactions for atomic operations
- Implement connection pooling for efficient resource usage

### 5. Real-time Updates
- Use WebSocket groups based on organization ID
- Implement proper authorization for group membership
- Use consistent event naming conventions
- Coordinate between Celery tasks and WebSocket notifications

## Code Organization

### 1. Application Structure
- Follow Django app-based organization
- Keep related functionality together
- Use clear naming conventions for files and directories

### 2. View Implementation
- Use class-based views when appropriate
- Implement proper permission mixins
- Document view parameters and return values

### 3. API Design
- Follow RESTful principles
- Implement proper versioning
- Document all endpoints with examples

## HTMX Patterns and Best Practices

### 1. Common HTMX Patterns
- Use `hx-get` for data retrieval operations
- Use `hx-post` for data modification operations
- Use `hx-trigger` for event-based interactions
- Implement `hx-indicator` for loading states

### 2. HTMX + Django Integration
- Create dedicated endpoints for HTMX requests
- Return HTML fragments from views
- Use Django template partials for consistent rendering
- Implement proper error handling for HTMX requests

### 3. HTMX + WebSocket Integration
- Use HTMX SSE or WebSocket extensions for real-time updates
- Implement server-sent events for one-way communication
- Use WebSockets for bidirectional communication
- Structure message handlers consistently

### 4. HTMX Performance Optimization
- Use `hx-boost` for page transitions
- Implement proper caching strategies
- Use `hx-swap-oob` for out-of-band swaps
- Minimize DOM updates for better performance

### 5. Converting JavaScript Components to HTMX
- Identify JavaScript-heavy components in the existing theme
- Create HTMX alternatives for common UI patterns
- Document conversion patterns for future reference
- Maintain a library of converted components

### 6. Sourcing Open Source HTMX Components
- Evaluate open source HTMX component libraries
- Maintain a list of vetted components for common UI patterns
- Document integration patterns for third-party components
- Contribute improvements back to the community

## Logging and Monitoring Standards

### 1. Application Logging
- Use structured logging with consistent fields
- Include organization context in all log entries
- Implement proper log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Configure separate log handlers for different environments

### 2. Celery Task Logging
- Log task start, completion, and failure events
- Include task ID, organization context, and correlation IDs in logs
- Implement task-specific logging with appropriate detail level
- Configure separate log files for Celery workers

### 3. Redis Monitoring
- Monitor Redis memory usage and connection count
- Set up alerts for Redis server issues
- Implement Redis key metrics collection
- Monitor Redis persistence and backup status

### 4. Performance Monitoring
- Implement request timing for critical views
- Monitor Celery task execution times
- Track WebSocket connection counts and message rates
- Set up alerting for performance degradation

## Testing Standards

### 1. Test Coverage
- Write tests for all models, views, and utilities
- Include multi-tenancy tests for all features
- Test both synchronous and asynchronous functionality
- Test HTMX interactions with proper request simulation
- Test Celery tasks with proper mocking

### 2. Test Organization
- Follow Django's test organization patterns
- Use fixtures for common test data
- Implement proper test isolation
- Create helper methods for common test scenarios
- Set up specific test cases for Celery tasks
- Always test with a script sent to Django management shell

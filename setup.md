# Migration Plan: neuralami-control to askanalytics

This document outlines the systematic approach to migrate essential components from the older `neuralami-control` project to the newer `askanalytics` project. The focus is on transferring baseline functionality while establishing modern patterns for future development.  the goal is to have a template for future apps with necessary infrastructure items that don't need to be redeveloped from app to app.  

## 1. Project Structure Analysis

### Current State
- **neuralami-control**: Older project with extensive functionality including multi-tenancy via the organizations app
- **askanalytics**: Newer project based on SoftUI Django Dashboard Pro template with basic functionality

### Target Components for Migration

#### Core Components
- Multi-tenancy (organizations app)
- Authentication system and user management
- Theme customizations with dark mode support
- Database configuration and secure storage
- SecureFileStorage for protected media files

#### Modern Architecture Components
- App-wide WebSocket support (Django Channels)
- HTMX-first approach (minimize JavaScript)
- Improved security patterns
- Enhanced logging and monitoring

## 2. Detailed Migration Steps

### 2.1. Core Settings Migration

1. **Update settings.py**
   - Merge essential settings from neuralami-control/core/settings.py to askanalytics/core/settings.py
   - Focus on:
     - Environment variable handling
     - Database configuration
     - Authentication backends
     - Middleware configuration
     - Logging setup
     - Storage configuration

2. **Update INSTALLED_APPS**
   - Add the organizations app to INSTALLED_APPS
   - Add channels and other required dependencies
   - Ensure all required dependencies are included

3. **Update Middleware**
   - Add organization middleware to the middleware stack
   - Include OrganizationMiddleware and OrganizationSecurityMiddleware

### 2.2. Organizations App Migration

1. **Copy the organizations app**
   - Copy the entire organizations app from neuralami-control to askanalytics
   - Include models, views, middleware, utils, and templates
   - Ensure all dependencies are properly handled

2. **Database Migrations**
   - Create initial migrations for the organizations app
   - Include migration for creating system roles and default organizations

3. **Update Templates**
   - Integrate organization templates with the SoftUI theme
   - Ensure organization switcher component works with the new theme
   - Add HTMX support for dynamic organization switching

### 2.3. Authentication System Migration

1. **Update User Model Integration**
   - Ensure proper integration between User model and Organization model
   - Verify that OrganizationMembership model works correctly

2. **Update Login/Registration Flow**
   - Modify login views to handle organization context
   - Update registration process to create default organization for new users
   - Enhance social authentication integration

3. **Update Permissions System**
   - Migrate role-based permissions system
   - Ensure proper integration with Django's permission system

### 2.4. Theme Customization

1. **Identify Theme Customizations**
   - Review custom CSS/JS in neuralami-control
   - Identify template overrides and custom components

2. **Apply Theme Customizations**
   - Apply identified customizations to askanalytics SoftUI theme
   - Implement dark mode toggle functionality
   - Ensure consistent look and feel across the application

### 2.5. Database and Storage Setup

1. **Update Database Configuration**
   - Ensure proper database settings for development and production
   - Migrate database connection handling from neuralami-control
   - Set up connection pooling for improved performance

2. **Implement SecureFileStorage**
   - Migrate SecureFileStorage class from neuralami-control
   - Configure proper access controls for media files
   - Set up storage backends for different environments
   - Implement protected file serving with authentication

3. **Create Database Migrations**
   - Create migrations for all new models
   - Test migrations to ensure data integrity

### 2.6. WebSocket Implementation

1. **Set up Django Channels**
   - Install and configure Django Channels
   - Set up ASGI application
   - Configure channel layers with Redis

2. **Create WebSocket Consumers**
   - Implement base WebSocket consumer
   - Create app-specific consumers as needed
   - Implement authentication and authorization for WebSockets

3. **Integrate WebSockets with UI**
   - Add WebSocket connection handling in templates
   - Create JavaScript utilities for WebSocket communication
   - Implement reconnection and error handling

### 2.7. HTMX Integration

1. **Set up HTMX Base Structure**
   - Add HTMX library to the project
   - Create base templates with HTMX support
   - Establish patterns for HTMX usage

2. **Convert Key Interactions to HTMX**
   - Identify JavaScript-heavy interactions
   - Replace with HTMX alternatives
   - Create reusable HTMX patterns

3. **Implement HTMX + WebSocket Integration**
   - Use HTMX SSE or WebSocket extensions
   - Create server-sent event endpoints
   - Implement real-time UI updates

4. **Theme Component Conversion**
   - Audit existing SoftUI Dashboard components that use JavaScript
   - Prioritize components for conversion based on usage frequency
   - Create HTMX alternatives for common components:
     - Data tables with sorting, filtering, and pagination
     - Modal dialogs and notifications
     - Form validation and submission
     - Tabs, accordions, and other interactive elements
   - Document conversion patterns for each component type

5. **Open Source Component Integration**
   - Research and evaluate HTMX-compatible component libraries
   - Test integration with the SoftUI theme
   - Create adapters for third-party components as needed
   - Maintain a catalog of approved components with usage examples

### 2.8. Testing

1. **Unit Tests**
   - Migrate relevant unit tests for organizations app
   - Create new tests for integrated functionality
   - Add tests for WebSocket consumers

2. **Integration Tests**
   - Test organization switching
   - Test multi-tenancy data isolation
   - Test authentication flows
   - Test WebSocket communication

3. **Manual Testing**
   - Verify UI components work correctly
   - Test user journeys for organization management
   - Test real-time functionality

## 3. Implementation Order

1. Core settings migration
2. Database and storage configuration
3. Organizations app migration
4. Authentication system integration
5. Theme customization
6. WebSocket implementation
7. HTMX integration
8. Testing and validation

## 4. Dependencies

- Django 4.2.x
- django-allauth (for authentication)
- django-redis (for caching)
- channels and channels-redis (for WebSocket support)
- htmx (for interactive UI with minimal JavaScript)
- django-storages (for cloud storage support)
- Other dependencies as needed from neuralami-control

## 5. Potential Challenges

1. **Data Model Differences**: The data models between the two projects might have evolved differently
2. **Theme Integration**: Ensuring the organizations app UI integrates well with SoftUI theme
3. **Dependency Conflicts**: Managing potential conflicts between dependencies
4. **Migration Complexity**: Ensuring smooth database migrations without data loss
5. **WebSocket Scaling**: Ensuring WebSocket implementation scales properly
6. **HTMX Learning Curve**: Team adaptation to HTMX-first approach

## 6. Production Deployment Process

### 6.1. Docker-based Deployment Architecture

1. **Container Components**
   - **Main Application Container**: Django application running with Uvicorn (ASGI server)
   - **Celery Worker Container**: For background task processing
   - **Celery Beat Container**: For scheduled tasks
   - **Redis Container**: For caching, session storage, and Celery broker

2. **Docker Image Building**
   - Use multi-stage builds for optimized images
   - Separate images for application and worker containers
   - Include version and commit information in image metadata
   - Implement proper health checks for all containers

3. **Environment Configuration**
   - Use environment variables for configuration
   - Store sensitive information in environment files
   - Implement different configurations for development and production

### 6.2. Deployment Workflow

1. **Build Process**
   ```bash
   # Update requirements
   uv pip freeze > requirements.txt

   # Build Docker images
   ./build-docker-images.sh
   ```

2. **Deployment Process**
   ```bash
   # Pull latest images
   docker-compose pull

   # Update services
   docker-compose up -d

   # Verify deployment
   docker-compose ps
   ```

3. **Database Migration Handling**
   - Run migrations during deployment with `RUN_MIGRATIONS=true`
   - Use entrypoint script to wait for database availability
   - Implement proper error handling for migration failures

### 6.3. Required Deployment Scripts

1. **build-docker-images.sh**
   - Script to build and tag Docker images
   - Includes version information from git
   - Pushes images to registry

2. **entrypoint.sh**
   - Container entrypoint script
   - Handles database connection verification
   - Runs migrations when configured
   - Sets up proper environment

3. **start_server.sh**
   - Starts the ASGI server (Uvicorn)
   - Configures WebSocket support
   - Sets proper worker parameters

4. **update-services.sh**
   - Pulls latest images
   - Updates running containers
   - Performs cleanup of old images

5. **docker-compose.yml**
   - Defines all services (app, worker, beat, redis)
   - Configures networking between services
   - Sets up volumes and environment variables
   - Implements health checks

### 6.4. Monitoring and Maintenance

1. **Health Checks**
   - Implement health check endpoints for all services
   - Configure Docker health checks for automatic recovery
   - Set up external monitoring for service availability

2. **Logging**
   - Centralize logs from all containers
   - Implement structured logging for easier analysis
   - Configure log rotation to prevent disk space issues

3. **Backup Strategy**
   - Regular database backups
   - Redis persistence configuration
   - Backup of environment configuration

### 6.5. Scaling Considerations

1. **Horizontal Scaling**
   - Scale application containers based on load
   - Configure Celery workers for different task types
   - Implement Redis clustering for high availability

2. **Resource Management**
   - Set appropriate resource limits for containers
   - Monitor resource usage and adjust as needed
   - Implement auto-scaling based on metrics

## 7. Post-Migration Tasks

1. **Documentation**: Update documentation to reflect the new structure
2. **Performance Testing**: Ensure the application performs well with the migrated components
3. **Security Review**: Conduct a security review of the migrated code
4. **User Training**: Provide guidance for users on any changes to the interface or functionality
5. **Monitoring Setup**: Implement proper monitoring for WebSockets and application performance

## 8. Rollback Plan

In case of critical issues during migration:
1. Document all changes made
2. Create backup points before major changes
3. Prepare rollback scripts for database migrations
4. Test rollback procedures before implementing major changes

## 9. Migration Checklist

### Phase 1: Core Infrastructure
- [ ] Update core settings
- [ ] Configure database connections
- [ ] Implement SecureFileStorage for protected media
- [ ] Set up protected file serving with authentication
- [ ] Configure Redis for caching, sessions, and message broker
- [ ] Set up Celery with proper task routing and monitoring
- [ ] Implement comprehensive logging for application and Celery tasks
- [ ] Set up monitoring for Redis and Celery workers

### Phase 2: Multi-tenancy
- [ ] Migrate organizations models
- [ ] Implement organization middleware
- [ ] Create organization templates
- [ ] Set up organization switching

### Phase 3: Authentication
- [ ] Update user profile model
- [ ] Integrate with organization system
- [ ] Enhance social authentication
- [ ] Implement role-based permissions

### Phase 4: UI and Interaction
- [ ] Implement theme customizations
- [ ] Add dark mode support
- [ ] Set up WebSocket infrastructure
- [ ] Implement HTMX patterns
- [ ] Audit JavaScript components for HTMX conversion
- [ ] Create HTMX alternatives for common UI components
- [ ] Research and integrate open source HTMX components
- [ ] Document component conversion patterns

### Phase 5: Testing and Deployment
- [ ] Run database migrations
- [ ] Execute unit tests
- [ ] Perform integration testing
- [ ] Create deployment scripts (build-docker-images.sh, entrypoint.sh, etc.)
- [ ] Set up Docker Compose configuration
- [ ] Configure CI/CD pipeline
- [ ] Deploy to staging environment
- [ ] Implement monitoring and health checks

## 9. Developer Standards and Best Practices

### UI Component Development

1. **HTMX-First Approach**
   - Use HTMX for interactive elements whenever possible
   - Minimize JavaScript to essential functionality only
   - Structure components to support progressive enhancement

2. **Component Structure**
   - Create reusable Django template partials in `templates/components/`
   - Use Django template inheritance for consistent layouts
   - Document component parameters and usage examples

3. **Styling Guidelines**
   - Follow BEM (Block Element Modifier) naming convention
   - Use CSS variables for theming (support light/dark modes)
   - Maintain responsive design principles

### Multi-tenancy Implementation

1. **Data Access Patterns**
   - Always use the organization-aware model managers
   - Never bypass the organization context in queries
   - Use `get_queryset()` overrides that respect organization boundaries

2. **File Access in Multi-tenant Context**
   - Always use SecureFileStorage for organization-specific files
   - Include organization context in file paths
   - Implement proper access control checks before serving files

3. **Cross-tenant Security**
   - Use the security middleware to prevent tenant data leakage
   - Implement explicit permission checks for all views
   - Audit all API endpoints for proper tenant isolation

### Asynchronous Operations

1. **WebSocket Standards**
   - Use authenticated WebSocket connections
   - Implement proper error handling and reconnection logic
   - Structure message formats consistently (JSON with action/payload pattern)

2. **Celery Task Standards**
   - Use Celery for all long-running operations
   - Include organization context in all task parameters
   - Implement proper error handling and retry mechanisms
   - Store task results with organization context
   - Use task routing for different task types
   - Implement task prioritization for critical operations

3. **Celery Configuration and Monitoring**
   - Configure Celery with Redis as the broker and result backend
   - Implement proper task logging with correlation IDs
   - Set up monitoring for Celery workers and queues
   - Configure task timeouts and rate limits appropriately
   - Implement dead letter queues for failed tasks

4. **Redis Usage Standards**
   - Use Redis for caching, session storage, and Celery broker
   - Implement proper key namespacing with organization context
   - Set appropriate TTL (time-to-live) for cached data
   - Use Redis transactions for atomic operations
   - Implement connection pooling for efficient resource usage

5. **Real-time Updates**
   - Use WebSocket groups based on organization ID
   - Implement proper authorization for group membership
   - Use consistent event naming conventions
   - Coordinate between Celery tasks and WebSocket notifications

### Code Organization

1. **Application Structure**
   - Follow Django app-based organization
   - Keep related functionality together
   - Use clear naming conventions for files and directories

2. **View Implementation**
   - Use class-based views when appropriate
   - Implement proper permission mixins
   - Document view parameters and return values

3. **API Design**
   - Follow RESTful principles
   - Implement proper versioning
   - Document all endpoints with examples

### HTMX Patterns and Best Practices

1. **Common HTMX Patterns**
   - Use `hx-get` for data retrieval operations
   - Use `hx-post` for data modification operations
   - Use `hx-trigger` for event-based interactions
   - Implement `hx-indicator` for loading states

2. **HTMX + Django Integration**
   - Create dedicated endpoints for HTMX requests
   - Return HTML fragments from views
   - Use Django template partials for consistent rendering
   - Implement proper error handling for HTMX requests

3. **HTMX + WebSocket Integration**
   - Use HTMX SSE or WebSocket extensions for real-time updates
   - Implement server-sent events for one-way communication
   - Use WebSockets for bidirectional communication
   - Structure message handlers consistently

4. **HTMX Performance Optimization**
   - Use `hx-boost` for page transitions
   - Implement proper caching strategies
   - Use `hx-swap-oob` for out-of-band swaps
   - Minimize DOM updates for better performance

5. **Converting JavaScript Components to HTMX**
   - Identify JavaScript-heavy components in the existing theme
   - Create HTMX alternatives for common UI patterns
   - Document conversion patterns for future reference
   - Maintain a library of converted components

6. **Sourcing Open Source HTMX Components**
   - Evaluate open source HTMX component libraries
   - Maintain a list of vetted components for common UI patterns
   - Document integration patterns for third-party components
   - Contribute improvements back to the community

### Logging and Monitoring Standards

1. **Application Logging**
   - Use structured logging with consistent fields
   - Include organization context in all log entries
   - Implement proper log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - Configure separate log handlers for different environments

2. **Celery Task Logging**
   - Log task start, completion, and failure events
   - Include task ID, organization context, and correlation IDs in logs
   - Implement task-specific logging with appropriate detail level
   - Configure separate log files for Celery workers

3. **Redis Monitoring**
   - Monitor Redis memory usage and connection count
   - Set up alerts for Redis server issues
   - Implement Redis key metrics collection
   - Monitor Redis persistence and backup status

4. **Performance Monitoring**
   - Implement request timing for critical views
   - Monitor Celery task execution times
   - Track WebSocket connection counts and message rates
   - Set up alerting for performance degradation

### Testing Standards

1. **Test Coverage**
   - Write tests for all models, views, and utilities
   - Include multi-tenancy tests for all features
   - Test both synchronous and asynchronous functionality
   - Test HTMX interactions with proper request simulation
   - Test Celery tasks with proper mocking

2. **Test Organization**
   - Follow Django's test organization patterns
   - Use fixtures for common test data
   - Implement proper test isolation
   - Create helper methods for common test scenarios
   - Set up specific test cases for Celery tasks

## 11. Memory and Notes

### Discoveries

_Add important discoveries and learnings here as we progress through the migration._

### Decisions

_Document key decisions made during the migration process._

### Open Questions

_Track questions that arise during migration that need further investigation._

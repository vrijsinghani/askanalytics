# Migration Plan

This document outlines the systematic approach to migrate essential components from the older `neuralami-control` project (located in the neuralami-control directory) to the newer `askanalytics` project.

## 1. Detailed Migration Steps

### 1.1. Core Settings Migration

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

### 1.2. Organizations App Migration

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

### 1.3. Authentication System Migration

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

### 1.4. Theme Customization

1. **Identify Theme Customizations**
   - Review custom CSS/JS in neuralami-control
   - Identify template overrides and custom components

2. **Apply Theme Customizations**
   - Apply identified customizations to askanalytics SoftUI theme
   - Implement dark mode toggle functionality
   - Ensure consistent look and feel across the application

### 1.5. Database and Storage Setup

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

### 1.6. WebSocket Implementation

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

### 1.7. HTMX Integration

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

### 1.8. Testing

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

## 2. Implementation Order

1. Core settings migration
2. Database and storage configuration
3. Organizations app migration
4. Authentication system integration
5. Theme customization
6. WebSocket implementation
7. HTMX integration
8. Testing and validation

## 3. Potential Challenges

1. **Data Model Differences**: The data models between the two projects might have evolved differently
2. **Theme Integration**: Ensuring the organizations app UI integrates well with SoftUI theme
3. **Dependency Conflicts**: Managing potential conflicts between dependencies
4. **Migration Complexity**: Ensuring smooth database migrations without data loss
5. **WebSocket Scaling**: Ensuring WebSocket implementation scales properly
6. **HTMX Learning Curve**: Team adaptation to HTMX-first approach

## 4. Rollback Plan

In case of critical issues during migration:
1. Document all changes made
2. Create backup points before major changes
3. Prepare rollback scripts for database migrations
4. Test rollback procedures before implementing major changes

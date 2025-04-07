# Memory and Notes

This document captures important discoveries, decisions, and open questions during the migration process.

## Discoveries

_Add important discoveries and learnings here as we progress through the migration._

### Core Infrastructure

- Implemented SecureFileStorage for protected media files with organization-aware access controls
- Set up WebSocket infrastructure with organization context support
- Configured Redis for multiple purposes: cache, session storage, and Celery broker
- Implemented comprehensive logging with separate handlers for different components
- Added connection pooling for database connections to improve performance
- Successfully tested core settings with a comprehensive test script
- Centralized Redis configuration with environment variables for consistent usage across components
- Created a proper testing structure with separate directories for unit tests, integration tests, and test scripts

### Multi-tenancy

- Successfully migrated the organizations app from neuralami-control to askanalytics
- Implemented organization middleware for both synchronous and asynchronous contexts
- Created organization templates for listing and managing organizations
- Set up organization switching functionality
- Implemented organization-based security to prevent cross-organization data leakage
- Added organization context utilities for both synchronous and asynchronous code

### Authentication

- Updated the user profile model to use SecureFileStorage for avatars
- Added token-based authentication for API access
- Integrated user profiles with the organization system
- Added methods to get a user's active organization and all organizations
- Created views and templates for API token management
- Implemented automatic token creation for new users

### UI and Interaction

- Implemented theme customizations with custom variables and CSS overrides
- Added dark mode support with persistence to both localStorage and user profile
- Set up WebSocket infrastructure with HTMX integration
- Created a real-time notification component using HTMX and WebSockets
- Added CSRF token handling for HTMX requests
- Improved theme initialization to prevent flickering when loading pages
- Created custom CSS fixes for dark mode and responsive design

### Deployment

-

## Decisions

_Document key decisions made during the migration process._

### Architecture Decisions

1. **Decision**: Use HTMX as the primary frontend interaction library
   - **Context**: Need to minimize JavaScript while maintaining interactive UI
   - **Alternatives Considered**: React, Vue.js, Alpine.js
   - **Reasoning**: HTMX provides a simpler, more maintainable approach that aligns with Django's server-side rendering

2. **Decision**: Use Django Channels for WebSocket support
   - **Context**: Need real-time communication capabilities
   - **Alternatives Considered**: Socket.IO, custom WebSocket implementation
   - **Reasoning**: Django Channels integrates well with the Django ecosystem and provides the necessary functionality

3. **Decision**: Use Celery with Redis for asynchronous tasks
   - **Context**: Need reliable background processing
   - **Alternatives Considered**: Django Q, Huey, Django Background Tasks
   - **Reasoning**: Celery is mature, well-documented, and provides the necessary features for our use case

### Implementation Decisions

1. **Decision**:
   - **Context**:
   - **Alternatives Considered**:
   - **Reasoning**:

## Open Questions

_Track questions that arise during migration that need further investigation._

1. **Question**:
   - **Context**:
   - **Potential Approaches**:
   - **Investigation Status**:

2. **Question**:
   - **Context**:
   - **Potential Approaches**:
   - **Investigation Status**:

3. **Question**:
   - **Context**:
   - **Potential Approaches**:
   - **Investigation Status**:

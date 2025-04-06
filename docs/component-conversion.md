# Component Conversion Guide

This document provides guidelines for converting JavaScript components to HTMX alternatives and sourcing components from open source projects.

## 1. JavaScript to HTMX Conversion Strategy

### 1.1. Component Audit Process

1. **Identify JavaScript Components**
   - Review all JavaScript files in the SoftUI Dashboard theme
   - Identify components that rely heavily on JavaScript
   - Categorize components by complexity and frequency of use

2. **Prioritization Criteria**
   - Frequency of use across the application
   - Complexity of the JavaScript implementation
   - Availability of HTMX alternatives
   - Impact on user experience

3. **Documentation Requirements**
   - Document original component behavior and requirements
   - Identify event handlers and state management needs
   - Note any third-party dependencies

### 1.2. Common Component Types and Conversion Patterns

#### Data Tables

**Original JavaScript Implementation:**
- Client-side sorting, filtering, and pagination
- Dynamic row updates
- Selection and bulk actions

**HTMX Conversion Pattern:**
- Server-side sorting with `hx-get` and sort parameters
- Filtering via form submission with `hx-post`
- Pagination with `hx-get` and page parameters
- Row selection with checkboxes and `hx-include`
- Bulk actions with `hx-post` and included form data

**Example:**
```html
<!-- Table with sorting -->
<table>
  <thead>
    <tr>
      <th hx-get="/data?sort=name" hx-target="tbody" hx-indicator="#spinner">
        Name
      </th>
      <!-- Other headers -->
    </tr>
  </thead>
  <tbody>
    <!-- Table rows -->
  </tbody>
</table>
<div id="spinner" class="htmx-indicator">Loading...</div>
```

#### Modal Dialogs

**Original JavaScript Implementation:**
- Dynamic content loading
- Show/hide functionality
- Form submission within modal

**HTMX Conversion Pattern:**
- Load modal content with `hx-get`
- Show modal with `hx-target` and CSS transitions
- Form submission with `hx-post` and response handling
- Close modal with `hx-on:click` or response headers

**Example:**
```html
<!-- Modal trigger -->
<button hx-get="/modal/content" hx-target="#modal-content">Open Modal</button>

<!-- Modal container -->
<div id="modal" class="modal">
  <div class="modal-content">
    <div id="modal-content"></div>
    <button hx-on:click="document.getElementById('modal').classList.remove('show')">Close</button>
  </div>
</div>
```

#### Form Validation

**Original JavaScript Implementation:**
- Client-side validation
- Dynamic error messages
- Form submission handling

**HTMX Conversion Pattern:**
- Server-side validation with immediate feedback
- Field-level validation with `hx-post` on input events
- Form submission with `hx-post` and error handling
- Use `hx-validate` extension for client-side validation

**Example:**
```html
<!-- Form with validation -->
<form hx-post="/submit" hx-swap="outerHTML">
  <div class="form-group">
    <input 
      name="email" 
      type="email" 
      hx-post="/validate/email" 
      hx-target="next .error-message" 
      hx-trigger="change">
    <div class="error-message"></div>
  </div>
  <!-- Other form fields -->
  <button type="submit">Submit</button>
</form>
```

#### Tabs and Accordions

**Original JavaScript Implementation:**
- Tab switching with active state
- Accordion expand/collapse
- Content loading

**HTMX Conversion Pattern:**
- Tab switching with `hx-get` and class toggling
- Accordion with `hx-get` and CSS transitions
- Lazy content loading with `hx-get`

**Example:**
```html
<!-- Tabs -->
<div class="tabs">
  <div class="tab-buttons">
    <button 
      hx-get="/tab/1" 
      hx-target="#tab-content" 
      class="active"
      hx-on:click="this.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active')); this.classList.add('active')">
      Tab 1
    </button>
    <!-- Other tab buttons -->
  </div>
  <div id="tab-content">
    <!-- Tab content loaded here -->
  </div>
</div>
```

#### Notifications and Alerts

**Original JavaScript Implementation:**
- Dynamic creation and display
- Auto-dismissal
- Animation effects

**HTMX Conversion Pattern:**
- Server-triggered notifications with `hx-swap-oob`
- Timed dismissal with CSS animations and `setTimeout`
- Notification queue management on the server

**Example:**
```html
<!-- Notification container -->
<div id="notifications">
  <!-- Notifications will be inserted here -->
</div>

<!-- Server response includes this -->
<div id="notifications" hx-swap-oob="beforeend">
  <div class="notification" hx-on:load="setTimeout(() => this.remove(), 5000)">
    Your changes have been saved!
  </div>
</div>
```

### 1.3. State Management Strategies

1. **Server-Side State**
   - Store state in the session or database
   - Use request parameters to maintain state
   - Implement proper caching for performance

2. **Client-Side State**
   - Use HTML attributes for simple state
   - Leverage localStorage for persistent state
   - Implement custom events for state changes

3. **Hybrid Approach**
   - Use server-side state for critical data
   - Use client-side state for UI preferences
   - Synchronize state when necessary

## 2. Open Source HTMX Components

### 2.1. Evaluation Criteria

1. **Quality Factors**
   - Code quality and maintainability
   - Documentation completeness
   - Test coverage
   - Active maintenance

2. **Integration Factors**
   - Compatibility with Django
   - Styling flexibility
   - Performance impact
   - Accessibility compliance

3. **Community Factors**
   - Community size and activity
   - Issue resolution time
   - Contribution guidelines
   - License compatibility

### 2.2. Recommended Component Libraries

#### HTMX Extensions

- **htmx-extensions**: Official extensions for HTMX
  - Client-side validation
  - Loading states
  - Class swapping
  - JSON encoding

#### UI Component Libraries

- **Hyperscript**: Scripting companion for HTMX
- **Alpine.js**: Minimal JavaScript framework for simple interactions
- **HTMX Bootstrap**: HTMX-compatible Bootstrap components
- **Django HTMX Components**: Reusable Django components with HTMX

#### Data Visualization

- **D3.js**: For complex visualizations with minimal JavaScript
- **Chart.js**: Simple charts with HTMX integration
- **HTMX-powered Datatables**: Server-side rendering of complex tables

### 2.3. Integration Patterns

1. **Django Template Integration**
   ```html
   {% include "components/htmx_datatable.html" with data=object_list %}
   ```

2. **Component Wrapper Pattern**
   ```python
   # In views.py
   def htmx_datatable(request):
       data = get_data(request.GET)
       if request.htmx:
           return render(request, "components/datatable_rows.html", {"data": data})
       return render(request, "components/datatable.html", {"data": data})
   ```

3. **Django Template Tag Pattern**
   ```python
   # In templatetags/htmx_components.py
   @register.inclusion_tag("components/modal.html")
   def htmx_modal(id, title, url):
       return {"id": id, "title": title, "url": url}
   ```

## 3. Component Library Development

### 3.1. Component Documentation Template

```markdown
# Component Name

## Description
Brief description of the component and its purpose.

## Usage
```html
<component-example></component-example>
```

## Parameters
- `param1`: Description of parameter 1
- `param2`: Description of parameter 2

## Events
- `event1`: Description of event 1
- `event2`: Description of event 2

## Examples
### Basic Example
```html
<example-code></example-code>
```

### Advanced Example
```html
<advanced-example></advanced-example>
```
```

### 3.2. Component Testing Strategy

1. **Unit Testing**
   - Test component rendering
   - Test HTMX interactions
   - Test server responses

2. **Integration Testing**
   - Test component in page context
   - Test interactions with other components
   - Test with real data

3. **Accessibility Testing**
   - Test keyboard navigation
   - Test screen reader compatibility
   - Test color contrast

### 3.3. Component Versioning and Maintenance

1. **Versioning Strategy**
   - Follow semantic versioning
   - Document breaking changes
   - Provide migration guides

2. **Maintenance Process**
   - Regular dependency updates
   - Performance optimization
   - Bug fix prioritization

3. **Contribution Guidelines**
   - Code style and formatting
   - Pull request process
   - Documentation requirements

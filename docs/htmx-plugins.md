# HTMX-Compatible Plugin Alternatives

This document provides an inventory of current JavaScript plugins used in the AskAnalytics project and suggests suitable open source alternatives that work well with an HTMX-first approach.

## Plugin Inventory and Alternatives

### Charts and Visualization

**Current: amcharts (Interactive charts and maps)**
- ⭐ **ApexCharts** - [https://apexcharts.com/](https://apexcharts.com/) - Highly Recommended
  - Lightweight, responsive, works well with HTMX, supports all common chart types
  - Best balance of features and performance
- Chart.js - [https://www.chartjs.org/](https://www.chartjs.org/)
  - Simpler API, smaller footprint than ApexCharts, good for basic charts
- ECharts - [https://echarts.apache.org/](https://echarts.apache.org/)
  - Apache project with extensive chart types including maps

**Current: chartjs.min.js (Charts and graphs)**
- ✅ **Chart.js** - [https://www.chartjs.org/](https://www.chartjs.org/) - Keep Current
  - Already lightweight and works well with HTMX

### Form Elements and UI Components

**Current: choices.min.js (Enhanced select boxes)**
- ⭐ **Slim Select** - [https://slimselectjs.com/](https://slimselectjs.com/) - Highly Recommended
  - Lightweight alternative with similar features
- Tom Select - [https://tom-select.js.org/](https://tom-select.js.org/)
  - Feature-rich select box enhancement, successor to selectize.js

**Current: countup.min.js (Animated number counting)**
- ✅ **CountUp.js** - [https://inorganik.github.io/countUp.js/](https://inorganik.github.io/countUp.js/) - Keep Current
  - Already using a good option, can be triggered via HTMX events

**Current: flatpickr.min.js (Date picker)**
- ✅ **Flatpickr** - [https://flatpickr.js.org/](https://flatpickr.js.org/) - Keep Current
  - Already lightweight and works well
- Pikaday - [https://github.com/Pikaday/Pikaday](https://github.com/Pikaday/Pikaday)
  - Consider only if Flatpickr has issues

**Current: nouislider.min.js (Range sliders)**
- ✅ **noUiSlider** - [https://refreshless.com/nouislider/](https://refreshless.com/nouislider/) - Keep Current
  - Best-in-class range slider

**Current: round-slider.min.js (Circular sliders)**
- ✅ **Round Slider** - [https://roundsliderui.com/](https://roundsliderui.com/) - Keep Current
  - Specialized component

### Data Tables

**Current: datatables.js (Interactive data tables)**
- ⭐ **Tabulator** - [http://tabulator.info/](http://tabulator.info/) - Highly Recommended
  - Feature-rich, responsive tables with sorting, filtering, and editing
  - Best balance of features and simplicity
- Grid.js - [https://gridjs.io/](https://gridjs.io/)
  - Lightweight table library with no dependencies
  - Good alternative for simpler tables
- AG Grid Community - [https://www.ag-grid.com/javascript-data-grid/getting-started/](https://www.ag-grid.com/javascript-data-grid/getting-started/)
  - Enterprise-grade grid with free community edition
  - Consider for complex enterprise requirements

### Drag and Drop

**Current: dragula (Drag and drop)**
- ⭐ **Sortable.js** - [https://sortablejs.github.io/Sortable/](https://sortablejs.github.io/Sortable/) - Highly Recommended
  - Lightweight drag-and-drop library with no jQuery dependency
  - More active development than Dragula
- DragSelect - [https://dragselect.com/](https://dragselect.com/)
  - For selection rather than drag-and-drop

### File Uploads

**Current: dropzone.min.js (File uploads)**
- ⭐ **Uppy** - [https://uppy.io/](https://uppy.io/) - Highly Recommended
  - Modern file uploader that works well with HTMX for final submission
  - Modern and feature-rich
- FilePond - [https://pqina.nl/filepond/](https://pqina.nl/filepond/)
  - Smooth file upload library with image preview
  - Good alternative with excellent UI

### Icons and Graphics

**Current: font-awesome6.4.0.min.js (Icons)**
- ⭐ **Phosphor Icons** - [https://phosphoricons.com/](https://phosphoricons.com/) - Highly Recommended
  - Modern icon set with flexible licensing
- Feather Icons - [https://feathericons.com/](https://feathericons.com/)
  - Simple, elegant open source icons

**Current: threejs.js (3D graphics)**
- ✅ **Three.js** - [https://threejs.org/](https://threejs.org/) - Keep Current
  - Best-in-class 3D library

**Current: orbit-controls.js (3D controls)**
- ✅ **Keep Current** - Required for Three.js

**Current: tilt.min.js (Tilt effects)**
- ⭐ **Vanilla-tilt.js** - [https://micku7zu.github.io/vanilla-tilt.js/](https://micku7zu.github.io/vanilla-tilt.js/) - Highly Recommended
  - Lightweight parallax tilt effect with no jQuery dependency

### Calendar and Date Handling

**Current: fullcalendar.min.js (Calendar)**
- ✅ **FullCalendar** - [https://fullcalendar.io/](https://fullcalendar.io/) - Keep Current
  - Best-in-class calendar

**Current: moment.min.js (Date manipulation)**
- ⭐ **Day.js** - [https://day.js.org/](https://day.js.org/) - Highly Recommended
  - 2KB alternative to Moment.js with compatible API
  - Much smaller than Moment.js
- Luxon - [https://moment.github.io/luxon/](https://moment.github.io/luxon/)
  - Modern replacement for Moment.js from same team
  - Good alternative with more features than Day.js

### Scrolling and UI Effects

**Current: perfect-scrollbar.min.js (Custom scrollbars)**
- ⭐ **Simplebar** - [https://github.com/Grsmto/simplebar](https://github.com/Grsmto/simplebar) - Highly Recommended
  - Lightweight custom scrollbar with native scroll behavior
  - Better performance
- Overlay Scrollbars - [https://kingsora.github.io/OverlayScrollbars/](https://kingsora.github.io/OverlayScrollbars/)
  - Lightweight scrollbar that hides native scrollbars

**Current: smooth-scrollbar.min.js (Custom scrolling)**
- ⭐ **Locomotive Scroll** - [https://locomotivemtl.github.io/locomotive-scroll/](https://locomotivemtl.github.io/locomotive-scroll/) - Highly Recommended
  - Smooth scrolling with parallax effects
- SmoothScroll - [https://github.com/gblazex/smoothscroll-for-websites](https://github.com/gblazex/smoothscroll-for-websites)
  - Simple smooth scrolling polyfill

### Notifications and Alerts

**Current: sweetalert.min.js (Alert dialogs)**
- ⭐ **SweetAlert2** - [https://sweetalert2.github.io/](https://sweetalert2.github.io/) - Highly Recommended
  - Modern replacement for SweetAlert with more features
- Notyf - [https://github.com/caroso1222/notyf](https://github.com/caroso1222/notyf)
  - Minimalistic toast notifications
- Toastify.js - [https://github.com/apvarun/toastify-js](https://github.com/apvarun/toastify-js)
  - Alternative for simple notifications

### Rich Text Editing

**Current: quill.min.js (Rich text editor)**
- ⭐ **Trix** - [https://trix-editor.org/](https://trix-editor.org/) - Highly Recommended
  - Simple, elegant rich text editor by Basecamp
- Editor.js - [https://editorjs.io/](https://editorjs.io/)
  - Block-styled editor with clean JSON output
- ProseMirror - [https://prosemirror.net/](https://prosemirror.net/)
  - Toolkit for building custom rich text editors

### Image Galleries

**Current: photoswipe.min.js (Image gallery)**
- ⭐ **Lightgallery.js** - [https://www.lightgalleryjs.com/](https://www.lightgalleryjs.com/) - Highly Recommended
  - Lightweight image gallery with no jQuery dependency
- Spotlight.js - [https://github.com/nextapps-de/spotlight](https://github.com/nextapps-de/spotlight)
  - Fast, lightweight image gallery

### Project Management

**Current: jkanban (Kanban boards)**
- ⭐ **Vanilla Kanban** - [https://github.com/yo-op/kanban](https://github.com/yo-op/kanban) - Highly Recommended
  - Lightweight Kanban board with no dependencies
- WeKan - [https://wekan.github.io/](https://wekan.github.io/)
  - Open source Kanban solution (more full-featured)

### Maps

**Current: leaflet.js (Interactive maps)**
- ✅ **Leaflet** - [https://leafletjs.com/](https://leafletjs.com/) - Keep Current
  - Best-in-class mapping library, already lightweight and open source

### Forms and Workflows

**Current: multistep-form.js (Multi-step forms)**
- ⭐ **HTMX + Alpine.js** - [https://alpinejs.dev/](https://alpinejs.dev/) - Highly Recommended
  - Use HTMX for navigation between steps and Alpine.js for state management
  - Perfect HTMX companion

### Core Libraries

**Current: htmx.min.js (HTMX core)**
- ✅ **HTMX** - [https://htmx.org/](https://htmx.org/) - Keep Current
  - Essential core library

**Current: ws.js (WebSockets)**
- ⭐ **HTMX SSE/WS Extensions** - [https://htmx.org/extensions/ws/](https://htmx.org/extensions/ws/) - Highly Recommended
  - Use HTMX's built-in WebSocket extension for native integration

## Recommended Core Libraries for HTMX Integration

For an HTMX-first approach, we recommend the following core set of libraries:

1. **HTMX** - Core library for HTML-driven AJAX
2. **Alpine.js** - Lightweight JS framework for adding behavior to HTML
3. **Tabulator** - For interactive data tables
4. **ApexCharts** or **Chart.js** - For data visualization
5. **SweetAlert2** or **Notyf** - For notifications and alerts
6. **Day.js** - Lightweight date manipulation (replacing Moment.js)
7. **Uppy** or **FilePond** - For enhanced file uploads

## Integration Patterns

When integrating these libraries with HTMX, follow these patterns:

1. **Server-Side Rendering**: Use Django to render the initial HTML structure
2. **Data Loading**: Use HTMX to load data from the server
3. **Client-Side Initialization**: Initialize the JavaScript library after data is loaded
4. **Event Handling**: Use HTMX events (htmx:afterSwap, etc.) to update the library when data changes

## Example: Tabulator with HTMX

```html
<!-- HTML Structure -->
<div id="data-table"></div>
<button hx-get="/api/refresh-data"
        hx-trigger="click"
        hx-target="#table-data-container"
        hx-swap="innerHTML">
    Refresh Data
</button>

<div id="table-data-container" hx-trigger="load" hx-get="/api/initial-data" style="display:none;">
    <!-- Data will be loaded here -->
</div>

<script>
// Initialize Tabulator after data is loaded
document.body.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === 'table-data-container') {
        // Parse the data from the container
        const tableData = JSON.parse(document.getElementById('table-data-container').textContent);

        // Initialize Tabulator
        new Tabulator("#data-table", {
            data: tableData,
            columns: [
                {title: "Name", field: "name"},
                {title: "Email", field: "email"},
                {title: "Status", field: "status"}
            ],
            pagination: "local",
            paginationSize: 10
        });
    }
});
</script>
```

## Example: ApexCharts with HTMX

```html
<div id="chart-container"></div>
<button hx-get="/api/chart-data"
        hx-trigger="click"
        hx-target="#chart-data-container"
        hx-swap="innerHTML">
    Update Chart
</button>

<div id="chart-data-container" hx-trigger="load" hx-get="/api/initial-chart-data" style="display:none;">
    <!-- Data will be loaded here -->
</div>

<script>
let chart;

// Initialize chart on page load
document.addEventListener('DOMContentLoaded', function() {
    chart = new ApexCharts(document.querySelector("#chart-container"), {
        chart: {
            type: 'line',
            height: 350
        },
        series: [{
            name: 'Sales',
            data: []
        }],
        xaxis: {
            categories: []
        }
    });
    chart.render();
});

// Update chart when data changes
document.body.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === 'chart-data-container') {
        const chartData = JSON.parse(document.getElementById('chart-data-container').textContent);
        chart.updateSeries([{
            name: 'Sales',
            data: chartData.values
        }]);
        chart.updateOptions({
            xaxis: {
                categories: chartData.categories
            }
        });
    }
});
</script>
```

## Example: SweetAlert2 with HTMX

```html
<button hx-post="/api/action"
        hx-trigger="click"
        hx-target="#result-container"
        hx-swap="innerHTML">
    Perform Action
</button>

<div id="result-container" style="display:none;"></div>

<script>
document.body.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === 'result-container') {
        const result = JSON.parse(document.getElementById('result-container').textContent);

        if (result.success) {
            Swal.fire({
                title: 'Success!',
                text: result.message,
                icon: 'success',
                confirmButtonText: 'OK'
            });
        } else {
            Swal.fire({
                title: 'Error!',
                text: result.message,
                icon: 'error',
                confirmButtonText: 'OK'
            });
        }
    }
});
</script>
```

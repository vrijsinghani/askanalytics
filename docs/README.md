# AskAnalytics Migration Documentation

This directory contains the documentation for migrating essential components from the older `neuralami-control` project to the newer `askanalytics` project.

## Documentation Structure

1. [**Migration Plan**](migration-plan.md) - Core migration steps and implementation order
2. [**Developer Standards**](developer-standards.md) - Coding standards, patterns, and best practices
3. [**Deployment Guide**](deployment-guide.md) - Production deployment process and scripts
4. [**Component Conversion**](component-conversion.md) - Guidelines for converting JS to HTMX
5. [**Checklist**](checklist.md) - Tracking progress with checkboxes
6. [**Memory**](memory.md) - Discoveries, decisions, and open questions

## Using This Documentation

### For Developers

- Start with the [Migration Plan](migration-plan.md) to understand the overall approach
- Refer to [Developer Standards](developer-standards.md) for coding guidelines
- Use [Component Conversion](component-conversion.md) when working with UI components

### For DevOps

- Use the [Deployment Guide](deployment-guide.md) for setting up production environments
- Follow the deployment scripts and configurations provided

### For Project Management

- Track progress using the [Checklist](checklist.md)
- Review decisions and open questions in the [Memory](memory.md) document

## For LLM Agents

This documentation is structured to be easily consumed by LLM agents. Each document focuses on a specific aspect of the migration process, making it easier to process and reason about the information.

When working with an LLM agent:

1. Point it to the specific document relevant to the current task
2. Ask it to update the [Memory](memory.md) document with any discoveries or decisions
3. Have it update the [Checklist](checklist.md) as tasks are completed

# Menu Planner Main Module Documentation

## Overview

The `main.py` module serves as the entry point and orchestration layer for the Menu Planner application. It implements a CrewAI Flow architecture to coordinate multiple specialized crews that handle different aspects of menu planning.

## Architecture

The application follows a modular architecture built on CrewAI Flow, with these key components:

1. **MenuFlow**: The central Flow class that orchestrates the entire menu generation process
2. **Specialized Crews**: Independent modules that handle specific tasks in the menu generation process
3. **Flow Routing**: Directional logic to guide the execution through different steps based on conditions
4. **Configuration System**: Centralized settings management using Pydantic models

## Key Components

### MenuFlow Class

The `MenuFlow` class extends CrewAI's `Flow` class and orchestrates the menu generation process with the following methods:

- **generate_menu**: Starting point (`@start`) that generates a complete menu or prepares for single recipe generation
- **route_menu_or_recipe**: Routes to either single recipe generation or full menu processing
- **generate_single_recipe**: Handles single recipe generation when specified by the user
- **check_state**: Verifies the menu state and routes to recipe preparation
- **route_after_recipes**: Routes to parallel generation of shopping list and HTML output
- **prepare_recipes**: Processes recipes in parallel with fallback to sequential processing
- **prepare_shopping_list**: Generates organized shopping lists from recipe ingredients
- **generate_html_output**: Creates an HTML presentation of the menu

### Error Handling

The application implements robust error handling throughout:

- Try/except blocks around all crew operations
- Detailed error logging with specific error messages
- Fallback mechanisms for critical operations (e.g., parallel processing)
- Initialization of empty structures when operations fail

### Flow Control

The flow supports two main execution paths:

1. **Full Menu Generation**:
   - Generates menu structure (MenuDesignerCrew)
   - Processes recipes in parallel (RecipeExpertCrew)
   - Generates shopping list (ShoppingCrew)
   - Creates HTML presentation (HtmlDesignCrew)

2. **Single Recipe Generation**:
   - Processes a single recipe (RecipeExpertCrew)

### Output Handling

The application handles crew outputs following CrewAI best practices:

- Direct attribute access (`result.task_name`) as the primary approach
- Multiple fallback mechanisms for backward compatibility
- Storage of results in the shared state
- Return of hashable types from flow methods to support proper routing

### Configuration

Configuration is centralized and managed through:

- Environment variables loaded via dotenv
- Pydantic models for validation and typing
- Default values for optional settings
- Configuration access via the global `config` object

## Execution Flow

1. Application starts at `kickoff()` function
2. `MenuFlow.generate_menu()` is executed as the start method
3. Based on the presence of `MaRecette`, routes to single recipe or full menu processing
4. For full menu processing:
   - Executes MenuDesignerCrew to create menu structure
   - Prepares recipes in parallel using RecipeExpertCrew
   - Routes to parallel execution of shopping list and HTML generation
5. For single recipe generation:
   - Executes RecipeExpertCrew for the specified recipe

## Optimization Features

- Parallel recipe processing using `kickoff_for_each()`
- Sequential fallback for error resilience
- Standardized file naming and organization
- Template variable initialization to avoid circular references

## Best Practices

- Proper logging with appropriate severity levels
- Comprehensive error handling and fallbacks
- Direct attribute access for crew outputs
- Return of hashable types from flow methods
- Modularity and separation of concerns
- Centralized configuration management

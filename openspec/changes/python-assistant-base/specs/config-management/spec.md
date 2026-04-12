## ADDED Requirements

### Requirement: Configuration model validation
The system SHALL provide Pydantic-based configuration classes with built-in validation.

#### Scenario: Configuration loading
- **WHEN** loading configuration
- **THEN** system reads from multiple sources: .env file, environment variables, config.yaml
- **AND** validates all required fields are present
- **AND** validates field types and formats
- **AND** raises ConfigurationError for invalid values

#### Scenario: Configuration access
- **WHEN** accessing configuration values
- **THEN** config.XXX provides typed access to configuration values
- **AND** config.get('nested.key') provides dot notation access
- **AND** config.has('key') checks for key existence
- **AND** all configuration access is immutable after loading

### Requirement: Environment-specific configuration
The system SHALL support different configuration profiles for different environments.

#### Scenario: Environment configuration
- **WHEN** loading configuration with environment flag
- **THEN** system loads config.{env}.yaml if it exists
- **AND** overrides base configuration with environment-specific values
- **AND** supports 'development', 'testing', 'production' environments
- **AND** raises RuntimeError for unknown environment

#### Scenario: Secret management
- **WHEN** loading secret configuration
- **THEN** API keys loaded from environment variables take precedence
- **AND** system never logs or prints secret values
- **AND** secret values are marked as such in configuration schema
- **AND** missing required secrets raise ConfigurationError
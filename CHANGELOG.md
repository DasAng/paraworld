# Change Log

## [1.1.1] - 

### Fixed

- High CPU usage in TaskRunner due to busy wait loop when checking completed tasks and timeout
- High CPU usage in running scenario steps when no concurrent steps are running

## [1.1.0] - 2022-02-27

### Added

- Support retrieving all feature files recursively from a directory
- Support filtering scenarios based on tags

### Changed

- TaskRunner.run() method can accept either a list of feature files or an instance of TaskRunnerConfig

## [1.0.0] - 2022-02-25

- Initial release

# Change Log

## [1.6.0] - 2022-05-19

### Changed

- Method to generate reports, junit, dependency and timeline files now supports specifying the name and location of the file

## [1.5.0] - 2022-05-18

### Breaking changes

- All step functions now requires an additional parameter named context of type ScenarioScope
- Context parameter allows for accessing and setting custom data that exists only in the current scenario

## [1.4.0] - 2022-05-18

### Added

- Before scenario and After scenario steps to be executed

## [1.3.0] - 2022-03-18

### Added

- Support generating JUnit XML report

## [1.2.0] - 2022-03-10

### Added

- Feedback system that allows you to be notified whenever a scenario or steps starts and completes

## [1.1.2] - 2022-03-05

### Fixed

- Optimize scenario to use less thread, when no concurrent steps are found

## [1.1.1] - 2022-03-03

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

# Tag Reference

*`This is the documentation for **Version 1.2.0**`*

**Table of contents**

- [@concurrent](#concurrent)
- [@depends](#depends)
- [@dependsGroups](#dependsgroups)
- [@id](#id)
- [@group](#group)
- [@parallel](#parallel)
- [@setup](#setup)
- [@teardown](#teardown)

# @concurrent

This tag can be applied to scenarios and will mark the scenario to be run concurrently. A concurrent scenario will be scheduled to run in another thread from the main thread.

*Syntax*:

`@concurrent`

*Example*:

```feature
Feature: Test concurrency

    @concurrent
    Scenario: Concurrent scenario 1
        Given a user
        When user signs in
        Then user should be authorized access

    @concurrent
    Scenario: Concurrent scenario 2
        Given another user
        When user fails to sign in
        Then user should be not be authorized access
```

# @depends

This tag can be applied to scenarios to mark the scenario as depending on another scenario. You normally use the [@id](#id) tag to specify the id of a scenario and then apply this @depends tag to specify the scenario of which you depends on. The scenario will only be scheduled to run once all the dependant scenarios have completed.

*Syntax*:

`@depends_<id>`

- \<id\> is the id of the scenario to depend on. The id only allows alphanumeric characters not including white spaces.

*Example*:

```feature
Feature: Test dependency

    @id_scenario1
    Scenario: scenario 1
        Given a user
        When user signs in
        Then user should be authorized access

    @depends_scenario1
    Scenario: scenario 2
        Given another user
        When user fails to sign in
        Then user should be not be authorized access
```

# @dependsGroups

This tag can be applied to scenarios to mark the scenario as depending on groups of scenarios. You normally use the [@group](#group) tag to specify the group name of a scenario and then apply this @dependsGroups tag to specify the scenario(s) of which you depends on. The scenario will only be scheduled to run once all the scenarios in a group have completed.

*Syntax*:

`@dependsGroups_<groupName>`

- \<groupName\> is the name of the group this scenario depends on. The group name only allows alphanumeric characters not including white spaces.

*Example*:

```feature
Feature: Test group dependency

    @group_login
    Scenario: scenario 1
        Given a user
        When user signs in
        Then user should be authorized access
    
    @group_login
    Scenario: scenario 2
        Given a user
        When user signs in
        Then user should be authorized access

    @dependsGroups_login
    Scenario: scenario 3
        Given another user
        When user fails to sign in
        Then user should be not be authorized access
```

# @id

This tag can be applied to scenarios to give the scenario an id that can be used by other scenarios that depends on this scenario. You normally use the [@id](#id) tag to specify the id of a scenario and then apply the [@depends](#depends) tag to specify the scenario of which depends on the scenario with the specified id.

*Syntax*:

`@id_<id>`

- \<id\> is the id of the scenario. The id only allows alphanumeric characters not including white spaces.

*Example*:

```feature
Feature: Test dependency

    @id_scenario1
    Scenario: scenario 1
        Given a user
        When user signs in
        Then user should be authorized access

    @depends_scenario1
    Scenario: scenario 2
        Given another user
        When user fails to sign in
        Then user should be not be authorized access
```

# @group

This tag can be applied to scenarios to mark the scenario as belonging to a group. Other scenarios can then be marked as depending on the group. You normally use the [@group](#group) tag to specify the name of the group for a scenario and then apply the [@dependsGroups](#dependsGroups) tag to specify the scenario of which depends on the group.

*Syntax*:

`@group_<groupName>`

- \<groupName\> is the name of the group this scenario is part of. The group name only allows alphanumeric characters not including white spaces.

*Example*:

```feature
Feature: Test group dependency

    @group_login
    Scenario: scenario 1
        Given a user
        When user signs in
        Then user should be authorized access
    
    @group_login
    Scenario: scenario 2
        Given a user
        When user signs in
        Then user should be authorized access

    @dependsGroups_login
    Scenario: scenario 3
        Given another user
        When user fails to sign in
        Then user should be not be authorized access
```

# @parallel

This tag can be applied to scenarios and will mark the scenario to be run in parallel. A parallel scenario will be scheduled to run in a separate process than the main process.

*Syntax*:

`@parallel`

*Example*:

```feature
Feature: Test parallel

    @parallel
    Scenario: Parallel scenario 1
        Given a user
        When user signs in
        Then user should be authorized access

    @parallel
    Scenario: Parallel scenario 2
        Given another user
        When user fails to sign in
        Then user should be not be authorized access
```

# @setup

This tag can be applied to scenarios and will mark the scenario to be run as part of a setup which means the scenario will be scheduled to run before all other non-setup scenarios.

*Syntax*:

`@setup`

*Example*:

```feature
Feature: Test setup

    @setup
    Scenario: scenario 1
        Given a user
        When user signs in
        Then user should be authorized access
```

# @teardown

This tag can be applied to scenarios and will mark the scenario to be run as part of a teardown which means the scenario will be scheduled to run after all other non-teardown scenarios have completed.

*Syntax*:

`@teardown`

*Example*:

```feature
Feature: Test teardown

    @teardown
    Scenario: scenario 1
        Then cleanup users
```
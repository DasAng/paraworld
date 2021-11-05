Feature: CPU intensive test with multiple threads

    Test running CPU intensive operation with multiple threads

    @concurrent
    Scenario: Compute PI
        Then calculate pi
    
    @concurrent
    Scenario: Compute PI 2
        Then calculate pi
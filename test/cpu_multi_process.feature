Feature: CPU intensive test with parallel process

    Test running CPU intensive operation with parallel process

    @parallel
    Scenario: Compute PI
        Then calculate pi
    
    @parallel
    Scenario: Compute PI 2
        Then calculate pi
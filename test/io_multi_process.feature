Feature: I/O test with multiple parallel process

    Test running network I/O request with multiple parallel process

    @parallel
    Scenario: Call a slow API
        Then call api
    
    @parallel
    Scenario: Call a slow API 2
        Then call api
# Steps

This is the documentation for **Version 1.1.0**

**paraworld** supports the following custom keywords that can be applied for steps that will change how the steps are being executed.


**Table of contents**

- [(background) Given](#background)
- [(background) When](#background)
- [(background) Then](#background)
- [(background) And](#background)
- [Concurrently](#concurrently)

# (background)

You can add the *(background)* keyword in front of *Given, When, Then, And* which will schedule the step to be run in a separate thread. This can be used to run steps concurrently.

Example:

```feature
Feature: concurrent steps test
  
  Scenario: set sister relationship
    
    this scenario will run in the same process as the main application process and in the same thread as the main thread.
    Creation of the users are done concurrently.

    (background) Given a user mary
    Given a user hans
    Then set mary as sister of hans
```

# Concurrently

Instead of using *Given, When, Then, And* you can use the keyword *Concurrently* which will schedule the step to be run in a separate thread. This can be used to run steps concurrently. Basically *Concurrently* is another way to write *(background) Given*.

Example:

```feature
Feature: concurrent steps test
  
  Scenario: set sister relationship
    
    this scenario will run in the same process as the main application process and in the same thread as the main thread.
    Creation of the users are done concurrently.

    Concurrently a user mary
    Given a user hans
    Then set mary as sister of hans
```

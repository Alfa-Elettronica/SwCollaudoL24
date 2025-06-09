# Exceptions

## Overview

This document provides an overview of custom exception handling in a Java-based application. It includes examples of how to define and use custom exceptions, as well as an implementation of a JWT authentication entry point to handle unauthorized access.

## JWT Authentication Entry Point

The `JwtAuthEntryPoint` class is responsible for handling unauthorized access attempts by sending an appropriate HTTP error response.

```java
import java.io.IOException;
@Component
public class JwtAuthEntryPoint implements AuthenticationEntryPoint {

    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response, AuthenticationException authException) throws IOException, ServletException {
        response.sendError(HttpServletResponse.SC_UNAUTHORIZED,"Bad Request");
    }
}
```

## Custom Exceptions

### BadRequestException

The `BadRequestException` class is a custom exception used to indicate that a bad request has been made.

```java
package com.ps.warehouse_service.exceptions;

public class BadRequestException extends RuntimeException {
    public BadRequestException(String message) {
        super(message);
    }
}
```

### InternalServerException

The `InternalServerException` class is a custom exception used to indicate that an internal server error has occurred.

```java
package com.ps.warehouse_service.exceptions;

public class InternalServerException extends RuntimeException {
    public InternalServerException(String message) {
        super(message);
    }
}
```
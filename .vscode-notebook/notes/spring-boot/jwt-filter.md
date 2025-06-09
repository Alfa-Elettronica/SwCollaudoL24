# JWT-Filter

## Overview

The `JwtFilter` class is a custom implementation of the `OncePerRequestFilter` provided by Spring Security. It is responsible for intercepting incoming HTTP requests and validating the JSON Web Token (JWT) present in the `Authorization` header. 

### Key Features:
- **Whitelist Support**: Skips filtering for URLs specified in the `URIConfig.WHITE_LISTED_URLS`.
- **Token Validation**: Extracts and validates the JWT token using the `JwtService`.
- **Authentication Setup**: Sets up the `SecurityContext` with the authenticated user's details if the token is valid.
- **Error Handling**: Responds with appropriate HTTP error codes for missing, invalid, or malformed tokens.

This filter ensures that only authenticated requests with valid JWT tokens can access protected resources in the application.


### JwtFilter
```java

@Component
public class JwtFilter extends OncePerRequestFilter {

    private static final Logger logger = LoggerFactory.getLogger(JwtFilter.class);
    private static final AntPathMatcher pathMatcher = new AntPathMatcher();

    private final JwtService jwtService;
    private final UserDetailsService userDetailsService;

    @Autowired
    public JwtFilter(JwtService jwtService, UserDetailsService userDetailsService) {
        this.jwtService = jwtService;
        this.userDetailsService = userDetailsService;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        String requestURI = request.getRequestURI();

        // Skip filter for whitelisted URLs
        for (String pattern : URIConfig.WHITE_LISTED_URLS) {
            if (pathMatcher.match(pattern, requestURI)) {
                logger.debug("Skipping JWT filter for whitelisted URL: {}", requestURI);
                filterChain.doFilter(request, response);
                return;
            }
        }

        String requestHeader = request.getHeader("Authorization");

        if (requestHeader == null || !requestHeader.startsWith("Bearer ")) {
            logger.warn("Missing or invalid Authorization header for request: {}", requestURI);
            response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Missing or invalid Authorization header");
            return;
        }

        try {
            String token = requestHeader.substring(7).trim();
            String username = jwtService.extractUsername(token);

            if (username != null && SecurityContextHolder.getContext().getAuthentication() == null) {
                User user = (User) userDetailsService.loadUserByUsername(username);

                if (jwtService.validateToken(token, user)) {
//                    logger.info("JWT authentication successful for user: {} ", user.getUsername());

                    UsernamePasswordAuthenticationToken authToken =
                            new UsernamePasswordAuthenticationToken(user.getUsername(), null,user.getAuthorities());
                    authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
                    SecurityContextHolder.getContext().setAuthentication(authToken);

                    logger.info("JWT authentication successful for user: {}", username);
//                    logger.info("Security Context Holder: {} ", SecurityContextHolder.getContext().getAuthentication().getAuthorities().stream().toList());

                } else {
                    logger.warn("JWT validation failed for user: {}", username);
                    response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Invalid JWT Token");
                    return;
                }
            }

        } catch (Exception e) {
            logger.error("Error parsing or validating JWT token", e);
            response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Invalid Token Format");
            return;
        }

        filterChain.doFilter(request, response);
    }
}

```
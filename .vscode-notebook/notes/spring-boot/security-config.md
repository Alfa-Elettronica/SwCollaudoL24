# Security Config

## Overview

This configuration file sets up the security for the application using Spring Security. It includes configurations for authentication, authorization, and JWT-based security.

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    // URLs that do not require authentication
    private static final String[] WHITE_LISTED_URLS = {
        "/auth/register",
        "/auth/login",
        "/h2-console",
        "/h2-console/**",
      
    };

    private final JwtFilter jwtAuthFilter;
    private final JwtAuthEntryPoint unauthorizedHandler;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    public SecurityConfig(JwtFilter jwtFilter, JwtAuthEntryPoint unauthorizedHandler) {
        this.jwtAuthFilter = jwtFilter;
        this.unauthorizedHandler = unauthorizedHandler;
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigures::disable)
            .authorizeHttpRequests(authRequest -> authRequest
                .requestMatchers(WHITE_LISTED_URLS).permitAll()
                .requestMatchers(HttpMethod.GET, "/products").hasRole("USER")
                .requestMatchers(HttpMethod.POST, "/products").hasRole("ADMIN")
                .requestMatchers(HttpMethod.PUT, "/products/**").hasRole("ADMIN")
                .requestMatchers(HttpMethod.DELETE, "/products/**").hasRole("ADMIN")
                .requestMatchers(HttpMethod.PATCH, "/products/**").hasRole("ADMIN")
                .requestMatchers(HttpMethod.POST, "/orders").hasRole("USER")
                .requestMatchers(HttpMethod.PUT, "/orders/**").hasRole("ADMIN")
                .requestMatchers(HttpMethod.PATCH, "/orders/**").hasRole("ADMIN")
                .requestMatchers(HttpMethod.DELETE, "/orders/**").hasAnyRole("USER", "ADMIN")
                .requestMatchers(HttpMethod.GET, "/orders/**").hasAnyRole("USER", "ADMIN")
                .anyRequest().authenticated()
            )
            .exceptionHandling(ex -> ex.authenticationEntryPoint(unauthorizedHandler))
            .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public AuthenticationProvider authenticationProvider(UserDetailsService userDetailsService) {
        DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
        provider.setUserDetailsService(userDetailsService);
        provider.setPasswordEncoder(passwordEncoder());
        return provider;
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration authConfig) throws Exception {
        return authConfig.getAuthenticationManager();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public UserDetailsService userDetailsService() {
        return username -> userRepository
                .findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException(
                        "User '" + username + "' not found"));
    }
}
```
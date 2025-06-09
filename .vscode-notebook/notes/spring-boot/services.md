# Services

## Overview

### Auth Service
```java

@Service
public class  AuthService {

    private static final Logger log = LoggerFactory.getLogger(AuthService.class);

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private JwtService jwtService;

    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    @Override
    public Optional<User> registerUser(RegisterPayload payload) {
        log.info("Attempting to register user: {}", payload.getUsername());
        User user = new User(
                payload.getUsername(),
                passwordEncoder.encode(payload.getPassword()),
                payload.getEmail(),
                new Role("ADMIN")    // assign default role
        );
        try {
            userRepository.save(user);
            log.info("User {} saved successfully", payload.getUsername());
            return userRepository.findByUsername(payload.getUsername());
        } catch (DataIntegrityViolationException dive) {
            // This catches unique‐constraint violations on username or email
            log.warn("Registration failed for {}: {}", payload.getUsername(), dive.getMostSpecificCause().getMessage());
            throw new BadRequestException("A user with that username or email already exists.");
        } catch (Exception e) {
            log.error("Unexpected error during registration for {}: {}", payload.getUsername(), e.getMessage(), e);
            throw new InternalServerException("Registration failed due to a server error.");
        }
    }

    @Override
    public Optional<String> loginUser(LoginPayload payload) {
        log.info("Login attempt for {}", payload.getUsername());
        try {
            User user = userRepository.findByUsername(payload.getUsername())
                    .orElseThrow(() -> new BadRequestException("Invalid username or password"));

            if (!passwordEncoder.matches(payload.getPassword(), user.getPassword())) {
                log.warn("Invalid password attempt for user: {}", payload.getUsername());
                throw new BadRequestException("Invalid username or password");
            }

            String token = jwtService.generateToken(user);
            log.info("Login successful for user: {}", payload.getUsername());
            return Optional.of(token);

        } catch (BadRequestException bre) {
            throw bre;  // let the global handler turn this into a 400
        } catch (Exception e) {
            log.error("Unexpected error during login for {}: {}", payload.getUsername(), e.getMessage(), e);
            throw new InternalServerException("Login failed due to a server error.");
        }
    }
}
```
### JWT SERVICE

```java
@Service
public class  JwtService {

    private static final Logger log = LoggerFactory.getLogger(JwtService.class);
    private final JwtConfig jwtConfig;

    @Autowired
    public JwtService(JwtConfig jwtConfig) {
        this.jwtConfig = jwtConfig;
    }

    private SecretKey getKey() {
//        log.info("The secret key : {}",jwtConfig.getSecretKey());
        return Keys.hmacShaKeyFor(jwtConfig.getSecretKey().getBytes(StandardCharsets.UTF_8));
    }

    private Claims getClaims(String token) {
        try {
//            return Jwts.parser()
//                    .setSigningKey(getKey())
//                    .build()
//                    .parseClaimsJws(token)
//                    .getBody();


            return Jwts.parser()
                    .verifyWith(getKey())
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();
        } catch (JwtException | IllegalArgumentException e) {
            log.error("Error parsing JWT token: {}", e.getMessage(), e);
            return null;
        }
    }

    @Override
    public String extractUsername(String token) {
        Claims claims = getClaims(token);
        return (claims != null) ? claims.getSubject() : null;
    }

    private Date getTokenExpiry(String token) {
        Claims claims = getClaims(token);
        return (claims != null) ? claims.getExpiration() : null;
    }

    @Override
    public boolean validateToken(String token, User user) {
        try {
            String username = extractUsername(token);
            Date expiry = getTokenExpiry(token);
            boolean isValid = username != null &&
                    username.equals(user.getUsername()) &&
                    expiry != null &&
                    expiry.after(new Date());

            if (!isValid) {
                log.warn("Token validation failed for user: {}", user.getUsername());
            }
            return isValid;
        } catch (Exception e) {
            log.error("Error during token validation: {}", e.getMessage(), e);
            return false;
        }
    }

    @Override
    public String generateToken(User user) {
        long nowMillis = System.currentTimeMillis();
        long expMillis = nowMillis + jwtConfig.getTokenExpiry() * 1000; // convert seconds to ms
//        List<String> roleNames = user.getAuthorities().stream()
//                .map(GrantedAuthority::getAuthority)
//                .toList();
//        return Jwts.builder()
//                .setIssuer(jwtConfig.getIssuer())
//                .setSubject(username)
//                .setIssuedAt(new Date(nowMillis))
//                .setExpiration(new Date(expMillis))
//                .signWith(getKey(), SignatureAlgorithm.HS256) // Ensure consistent algorithm
//                .compact();

                return Jwts.builder()
                            .issuer(jwtConfig.getIssuer())
                            .subject(user.getUsername())
                            .issuedAt(new Date(nowMillis))
                            .expiration(new Date(expMillis))
                            .signWith(getKey())
                            .compact();


    }
}

```

### Order Service

```java


@Service
public class OrderService {

    private static final Logger logger = LoggerFactory.getLogger(OrderService.class);

    private final OrderRepository orderRepository;

    @Autowired
    public OrderService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
    }

    @Override
    public Order createOrder(OrderRequest request) {
        logger.info("Creating order with details: {}", request);
        Order order = new Order();
        // Set the necessary fields from OrderRequest to Order entity
        order.setCreatedBy(request.getCreatedBy());
        order.setSubmittedDate(new Date());
        order.setModifiedDate(new Date());
        order.setExecutionDate(request.getExecutionDate());
        // Set products if present in the request (you'll have to populate this in a real scenario)
        // order.setProducts(request.getProducts());

        Order savedOrder = orderRepository.save(order);
        logger.info("Order created successfully with ID: {}", savedOrder.getOrderId());
        return savedOrder;
    }

    @Override
    public Order getOrderById(String orderId) {
        logger.info("Fetching order with ID: {}", orderId);
        Optional<Order> order = orderRepository.findById(orderId);
        if (order.isPresent()) {
            logger.info("Order found with ID: {}", order.get().getOrderId());
            return order.get();
        } else {
            logger.warn("Order with ID: {} not found", orderId);
            return null;
        }
    }

    @Override
    public List<Order> getAllOrders() {
        logger.info("Fetching all orders");
        List<Order> orders = orderRepository.findAll();
        logger.info("Found {} orders", orders.size());
        return orders;
    }

    @Override
    public Order updateOrderStatus(String orderId, String status) {
        logger.info("Updating status for order with ID: {} to {}", orderId, status);
        Optional<Order> existingOrder = orderRepository.findById(orderId);
        if (existingOrder.isPresent()) {
            Order order = existingOrder.get();
            // Assuming you have a 'status' field in the Order entity, which is not defined in the original class
            order.setStatus(status);

            Order updatedOrder = orderRepository.save(order);
            logger.info("Order status updated successfully for Order ID: {}", updatedOrder.getOrderId());
            return updatedOrder;
        } else {
            logger.warn("Order with ID: {} not found for status update", orderId);
            return null;
        }
    }

    @Override
    public void deleteOrder(String orderId) {
        logger.info("Deleting order with ID: {}", orderId);
        if (orderRepository.existsById(orderId)) {
            orderRepository.deleteById(orderId);
            logger.info("Order with ID: {} deleted successfully", orderId);
        } else {
            logger.warn("Order with ID: {} not found for deletion", orderId);
        }
    }
}

```
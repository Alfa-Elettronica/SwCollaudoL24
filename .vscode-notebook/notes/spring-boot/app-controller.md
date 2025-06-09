# App Controller

## Overview

This file contains the implementation of the `OrderController` class, which serves as the REST controller for managing orders in the application. It provides endpoints for creating, retrieving, updating, and deleting orders. The controller uses the `OrderService` to handle business logic and interacts with the client through HTTP requests and responses.

### Key Features:
- **Create Order**: Handles `POST` requests to create a new order.
- **Retrieve Order by ID**: Handles `GET` requests to fetch a specific order by its ID.
- **Retrieve All Orders**: Handles `GET` requests to fetch all orders.
- **Update Order Status**: Handles `PUT` requests to update the status of an order.
- **Delete Order**: Handles `DELETE` requests to remove an order by its ID.

### Error Handling:
The controller includes exception handling for various scenarios, such as:
- Internal server errors during order creation or retrieval.
- Resource not found errors when an order does not exist.
- Bad request errors for invalid updates.

### Logging:
The `Logger` is used to log errors and provide insights into the application's behavior during runtime.

```java


@RestController
@RequestMapping("/orders")
public class OrderController {

    private final OrderService orderService;
    private static final Logger logger = LoggerFactory.getLogger(OrderController.class);

    @Autowired
    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @PostMapping
    public ResponseEntity<?> createOrder(@RequestBody OrderRequest request) throws InternalServerException {
        try {
            Order newOrder = orderService.createOrder(request);
            return ResponseEntity.ok(newOrder);
        } catch (Exception e) {
            logger.error("Error creating order: {}", e.getMessage());
            throw new InternalServerException("Failed to create order: " + e.getMessage());
        }
    }

    @GetMapping("/{id}")
    public ResponseEntity<?> getOrderById(@PathVariable String id) throws InternalServerException {
        try {
            Order order = orderService.getOrderById(id);
            if (order == null) {
                throw new ResourceNotFoundException("Order not found with ID: " + id);
            }
            return ResponseEntity.ok(order);
        } catch (Exception | ResourceNotFoundException e) {
            logger.error("Error fetching order: {}", e.getMessage());
            throw new InternalServerException("Failed to fetch order: " + e.getMessage());
        }
    }

    @GetMapping
    public ResponseEntity<?> getAllOrders() throws InternalServerException {
        try {
            List<Order> orders = orderService.getAllOrders();
            return ResponseEntity.ok(orders);
        } catch (Exception e) {
            logger.error("Error fetching orders: {}", e.getMessage());
            throw new InternalServerException("Failed to fetch orders: " + e.getMessage());
        }
    }

    @PutMapping("/{id}/status")
    public ResponseEntity<?> updateOrderStatus(@PathVariable String id, @RequestParam String status) throws BadRequestException {
        try {
            Order updated = orderService.updateOrderStatus(id, status);
            if (updated == null) {
                throw new ResourceNotFoundException("Order not found with ID: " + id);
            }
            return ResponseEntity.ok(updated);
        } catch (Exception e) {
            logger.error("Error updating order status: {}", e.getMessage());
            throw new BadRequestException("Failed to update order status: " + e.getMessage());
        } catch (ResourceNotFoundException e) {
            throw new RuntimeException(e);
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteOrder(@PathVariable String id) throws ResourceNotFoundException {
        try {
            orderService.deleteOrder(id);
            return ResponseEntity.noContent().build();
        } catch (Exception e) {
            logger.error("Error deleting order: {}", e.getMessage());
            throw new ResourceNotFoundException("Failed to delete order with ID: " + id);
        }
    }
}
```
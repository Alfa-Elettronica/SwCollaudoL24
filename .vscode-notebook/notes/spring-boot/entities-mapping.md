# Entities

## Overview

The code defines two Java classes, User and Role, which represent entities in a database. These entities are part of a system that uses Spring Data JPA for object-relational mapping (ORM). The User class represents application users, while the Role class represents roles assigned to users. Both classes are annotated with JPA annotations to map them to database tables.
```java
@ManyToMany(fetch = FetchType.EAGER, cascade = CascadeType.ALL)
@JoinTable(
    name = "user_roles",
    joinColumns = @JoinColumn(name = "user_id"),
    inverseJoinColumns = @JoinColumn(name = "role_id")
)
private Set<Role> roles = new HashSet<>();
```
@ManyToMany: Defines a many-to-many relationship between User and Role.
fetch = FetchType.EAGER: Ensures roles are loaded immediately with the user.
cascade = CascadeType.ALL: Propagates all operations (e.g., persist, remove) to the related roles.
@JoinTable: Specifies the join table (user_roles) and the foreign key columns (user_id and role_id).

```java
@OneToMany(mappedBy = "createdBy", cascade = CascadeType.ALL, orphanRemoval = true)
private List<Order> orders = new ArrayList<>();
```
@OneToMany: Defines a one-to-many relationship between User and Order.
mappedBy = "createdBy": Indicates that the createdBy field in the Order class owns the relationship.
orphanRemoval = true: Automatically removes orders if they are no longer associated with a user.



### User
```java

@Entity
@Table(name = "users")
public class User implements UserDetails {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long userId;

    @Column(unique = true, nullable = false)
    private String username;

    @Column(nullable = false)
    private String password;

    @Column(unique = true, nullable = false)
    private String email;

    @ManyToMany(fetch = FetchType.EAGER, cascade = CascadeType.ALL)
    @JoinTable(
            name = "user_roles",
            joinColumns = @JoinColumn(name = "user_id"),
            inverseJoinColumns = @JoinColumn(name = "role_id")
    )
    private Set<Role> roles = new HashSet<>();

    @OneToMany(mappedBy = "createdBy", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Order> orders = new ArrayList<>();

    public User(String username, String password, String email, Role role) {
        this.username = username;
        this.password = password;
        this.email = email;
        this.roles.add(role);
    }

    public User() {

    }



    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {

        return roles.stream().toList();
    }

    @Override
    public String getPassword() {
        return this.password;
    }

    @Override
    public String getUsername() {
        return this.username;
    }

    public String getEmail() {
        return this.email;
    }
}
```


### Role

```java


@Entity
@Table(name = "roles")
public class Role implements GrantedAuthority {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long roleId;

    @Column(nullable = false, unique = true)
    private String authority;

    @ManyToMany(mappedBy = "roles", fetch = FetchType.LAZY)
    private Set<User> users = new HashSet<>();

    @ElementCollection(fetch = FetchType.EAGER)
    @CollectionTable(name = "role_permissions", joinColumns = @JoinColumn(name = "role_id"))
    @Column(name = "permission")
    private List<String> permissions = new ArrayList<>();

    public Role() {

    }

    public Role(String authority) {
        this.authority = authority;
        this.permissions.add("READ");
        this.permissions.add("WRITE");
    }

    @Override
    public String getAuthority() {
        if (authority != null && authority.startsWith("ROLE_")) {
            return authority;
        }
        return "ROLE_" + authority;
    }

    // Getters and Setters
    public Long getRoleId() {
        return roleId;
    }

    public void setRoleId(Long roleId) {
        this.roleId = roleId;
    }

    public void setAuthority(String authority) {
        this.authority = authority;
    }

    public Set<User> getUsers() {
        return users;
    }

    public void setUsers(Set<User> users) {
        this.users = users;
    }

    public List<String> getPermissions() {
        return permissions;
    }

    public void setPermissions(List<String> permissions) {
        this.permissions = permissions;
    }
}

```
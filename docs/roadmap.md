# StxScript Development Roadmap

This roadmap outlines the planned development phases for StxScript, focusing on building a solid, practical transpiler for Stacks blockchain development.

## 🎯 Current Status (v0.1.0 - Alpha)

**✅ Completed:**
- Core transpiler infrastructure with Lark parser
- Basic variable and constant declarations
- Type system for primitive types (`int`, `uint`, `string`, `boolean`, `principal`)
- Function signature declarations with decorators (`@public`, `@readable`)
- Command-line interface with file I/O
- Python API for programmatic use
- Comprehensive documentation and examples

**📊 Current Capabilities:**
```typescript
// These work today ✅
const TOKEN_NAME: string = "MyToken";
let balance: uint = 1000u;

@public
function transfer(to: principal, amount: uint): Response<bool, string> {
    // Signature only - body implementation coming in Phase 1
}
```

## 📈 Development Phases

### Phase 1: Expression System (v0.2.0 - Beta)
**Target: Q1 2024 | Estimated: 4-6 weeks**

Core goal: Enable basic expressions and function bodies

**🎯 Deliverables:**
- **Arithmetic expressions**: `+`, `-`, `*`, `/`, `%`
- **Comparison operators**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Logical operators**: `&&`, `||`, `!`
- **Assignment operations**: Variable updates
- **Function calls**: Basic function invocation
- **Return statements**: Function return values

**🔧 Technical Tasks:**
1. Extend grammar for expression parsing
2. Implement expression evaluation in transformer
3. Add operator precedence handling
4. Enable basic function body implementation
5. Add expression validation and type checking

**📝 Example Target:**
```typescript
@public
function add(a: uint, b: uint): uint {
    return a + b;  // ✅ Will work in Phase 1
}

function validate_amount(amount: uint): boolean {
    return amount > 0u && amount <= 1000000u;  // ✅ Will work
}
```

**🧪 Success Criteria:**
- [ ] All arithmetic operations transpile correctly
- [ ] Function bodies with expressions work
- [ ] Type checking prevents invalid operations
- [ ] At least 50 test cases pass

---

### Phase 2: Control Flow (v0.3.0 - Beta)
**Target: Q2 2024 | Estimated: 3-4 weeks**

Core goal: Add conditional logic and basic control structures

**🎯 Deliverables:**
- **If/else statements**: Conditional execution
- **Match expressions**: Pattern matching (Clarity's `match`)
- **Let bindings**: Local variable scoping
- **Error propagation**: `unwrap!` and `try!` equivalents

**🔧 Technical Tasks:**
1. Implement if/else statement parsing and generation
2. Add match expression support for Response and Optional types
3. Implement local variable scoping with `let`
4. Add error handling constructs

**📝 Example Target:**
```typescript
@public
function safe_transfer(amount: uint, to: principal): Response<bool, string> {
    if (amount == 0u) {
        return err("Amount cannot be zero");
    }

    let current_balance = get_balance(tx.sender);
    if (current_balance < amount) {
        return err("Insufficient balance");
    }

    set_balance(tx.sender, current_balance - amount);
    set_balance(to, get_balance(to) + amount);
    return ok(true);
}
```

**🧪 Success Criteria:**
- [ ] Nested if/else statements work correctly
- [ ] Match expressions handle Response/Optional types
- [ ] Local scoping doesn't conflict with global variables
- [ ] Error handling integrates with Clarity semantics

---

### Phase 3: Data Structures (v0.4.0 - Stable)
**Target: Q3 2024 | Estimated: 4-5 weeks**

Core goal: Support Lists, Tuples, and basic Maps

**🎯 Deliverables:**
- **List operations**: Creation, indexing, iteration
- **Tuple support**: Named and positional access
- **Map declarations**: Basic map operations
- **Optional types**: `some()`, `none()`, unwrapping
- **Response types**: `ok()`, `err()`, error handling

**🔧 Technical Tasks:**
1. Implement list literal syntax and operations
2. Add tuple creation and destructuring
3. Basic map syntax (read-only initially)
4. Optional and Response type handling
5. Iterator-like operations (`map`, `filter`, `fold`)

**📝 Example Target:**
```typescript
// List operations
let numbers: list<uint> = [1u, 2u, 3u, 4u, 5u];
let doubled = map(numbers, (x) => x * 2u);
let evens = filter(numbers, (x) => x % 2u == 0u);

// Tuple handling
let user: {name: string, balance: uint} = {
    name: "Alice",
    balance: 1000u
};

// Optional types
let maybe_balance: optional<uint> = get_balance_safe(user.name);
match maybe_balance {
    some(balance) => balance,
    none => 0u
}

// Basic map usage (read-only)
@map
const balances: Map<principal, uint>;

@readable
function get_balance(account: principal): uint {
    return balances.get(account).unwrap_or(0u);
}
```

**🧪 Success Criteria:**
- [ ] List operations transpile to correct Clarity
- [ ] Tuple access works for named and indexed access
- [ ] Optional/Response types integrate properly
- [ ] Map reading operations work (writing in Phase 4)

---

### Phase 4: Advanced Language Features (v0.5.0 - Stable)
**Target: Q4 2024 | Estimated: 5-6 weeks**

Core goal: Complete core language feature set

**🎯 Deliverables:**
- **Map mutations**: Insert, update, delete operations
- **Lambda expressions**: Anonymous functions
- **Type inference improvements**: Better automatic typing
- **Import/export**: Module system basics
- **Trait definitions**: Interface contracts

**🔧 Technical Tasks:**
1. Implement map mutation operations
2. Add lambda expression parsing and generation
3. Improve type inference engine
4. Basic module system for code organization
5. Trait definition and implementation checking

**📝 Example Target:**
```typescript
// Map mutations
@map
let balances: Map<principal, uint> = new Map();

@public
function mint(to: principal, amount: uint): Response<bool, string> {
    let current = balances.get(to).unwrap_or(0u);
    balances.set(to, current + amount);
    return ok(true);
}

// Lambda expressions
let validators = [
    (x: uint) => x > 0u,
    (x: uint) => x <= MAX_SUPPLY,
    (x: uint) => x % 1000u == 0u
];

let is_valid = validators.all((validator) => validator(amount));

// Trait usage
trait Transferable {
    transfer(from: principal, to: principal, amount: uint): Response<bool, string>;
    get_balance(account: principal): uint;
}

class Token implements Transferable {
    // Implementation
}
```

**🧪 Success Criteria:**
- [ ] Map operations work correctly with state changes
- [ ] Lambda expressions integrate with built-in functions
- [ ] Type inference reduces annotation requirements by 50%
- [ ] Basic trait system enables interface contracts

---

### Phase 5: Developer Experience (v1.0.0 - Production)
**Target: Q1 2025 | Estimated: 4-6 weeks**

Core goal: Production-ready tooling and developer experience

**🎯 Deliverables:**
- **Enhanced error messages**: Clear, actionable error reporting
- **Language server**: IDE integration (VS Code extension)
- **Formatter**: Code formatting tool (`stxscript fmt`)
- **Linter**: Static analysis and best practices
- **Package manager**: Dependency management
- **Documentation generator**: Auto-generate docs from code

**🔧 Technical Tasks:**
1. Implement detailed error reporting with suggestions
2. Create Language Server Protocol (LSP) implementation
3. Build code formatter with configurable styles
4. Add linting rules for common mistakes
5. Basic package/module management system
6. Documentation extraction from comments

**📝 Example Target:**
```bash
# Enhanced tooling
stxscript fmt contract.stx           # Format code
stxscript lint contract.stx          # Check for issues
stxscript doc contract.stx           # Generate documentation
stxscript install some-package       # Install dependencies

# VS Code integration
# - Syntax highlighting
# - Error squiggles
# - Auto-completion
# - Go to definition
```

**🧪 Success Criteria:**
- [ ] Error messages include fix suggestions
- [ ] VS Code extension provides full language support
- [ ] Formatter handles complex code structures
- [ ] Linter catches 90% of common mistakes
- [ ] Package system enables code reuse

---

## 🎯 Key Milestones

| Milestone | Version | Timeline | Core Feature |
|-----------|---------|----------|--------------|
| **Expression Engine** | v0.2.0 | Q1 2024 | Basic expressions and function bodies |
| **Control Flow** | v0.3.0 | Q2 2024 | If/else, match, error handling |
| **Data Structures** | v0.4.0 | Q3 2024 | Lists, tuples, maps, optionals |
| **Advanced Features** | v0.5.0 | Q4 2024 | Lambdas, traits, modules |
| **Production Ready** | v1.0.0 | Q1 2025 | Full tooling and IDE support |

## 🚀 Implementation Priorities

### High Priority (Essential for Beta)
1. **Expression evaluation** - Core to any practical use
2. **Function implementations** - Enable real contract logic
3. **If/else statements** - Basic conditional logic
4. **Error handling** - Critical for Clarity contracts
5. **List operations** - Common data structure need

### Medium Priority (Important for Stability)
1. **Map operations** - Clarity's primary data structure
2. **Type inference improvements** - Better developer experience
3. **Lambda expressions** - Functional programming support
4. **Local variable scoping** - Proper variable management

### Lower Priority (Nice to Have)
1. **Trait system** - Advanced type system features
2. **Module system** - Code organization
3. **Advanced tooling** - IDE integration, formatting

## 🤝 Community Involvement

### How Contributors Can Help

**Phase 1 (Expression System):**
- **Grammar experts**: Help refine expression parsing
- **Clarity developers**: Validate output correctness
- **Test writers**: Create comprehensive test suites

**Phase 2 (Control Flow):**
- **Language designers**: Design match expression syntax
- **Error handling specialists**: Clarity error pattern experts

**Phase 3 (Data Structures):**
- **Data structure implementers**: List/tuple operations
- **Clarity map experts**: Map operation best practices

**Phase 4+ (Advanced Features):**
- **Type system designers**: Trait and inference systems
- **Tooling developers**: IDE integration and language servers

### Contribution Areas by Skill Level

**🟢 Beginner Friendly:**
- Writing test cases for new features
- Improving documentation and examples
- Adding grammar rules for simple constructs
- Bug fixes in existing functionality

**🟡 Intermediate:**
- Implementing transformer methods for new AST nodes
- Adding new operators and expressions
- Error message improvements
- CLI enhancements

**🔴 Advanced:**
- Core grammar design and conflict resolution
- Type inference engine improvements
- Language server implementation
- Performance optimization

## 📊 Success Metrics

### Technical Metrics
- **Test coverage**: Maintain >90% code coverage
- **Grammar conflicts**: Zero shift/reduce conflicts
- **Performance**: <100ms transpilation for typical contracts
- **Clarity compatibility**: 100% valid output

### Community Metrics
- **GitHub stars**: 500+ by v1.0
- **Contributors**: 20+ active contributors
- **Contracts transpiled**: 100+ real contracts in production
- **Documentation**: Complete with examples for all features

### Adoption Metrics
- **Package downloads**: 1000+ monthly downloads
- **IDE usage**: VS Code extension with 500+ installs
- **Community projects**: 10+ projects using StxScript

## 🔄 Release Strategy

### Version Numbering
- **Major versions** (1.0, 2.0): Breaking changes, major features
- **Minor versions** (0.1, 0.2): New features, backward compatible
- **Patch versions** (0.1.1, 0.1.2): Bug fixes, small improvements

### Release Cadence
- **Major releases**: Every 6-12 months
- **Minor releases**: Every 4-6 weeks during active development
- **Patch releases**: As needed for critical fixes

### Feature Flags
- **Experimental features**: Available behind flags for testing
- **Beta features**: Stable API, may have minor changes
- **Stable features**: Production ready, breaking changes require major version

## 📝 Future Considerations (Beyond v1.0)

### Potential Advanced Features
- **Async/await patterns**: For contract interactions
- **Generic types**: Parameterized types and functions
- **Macros**: Code generation capabilities
- **Static analysis**: Advanced type checking and optimization
- **Cross-contract calls**: Enhanced contract interaction syntax
- **Testing framework**: Built-in testing DSL
- **Deployment tools**: Integrated deployment and testing

### Language Extensions
- **SQL-like syntax**: For data querying
- **React-like patterns**: For frontend integration
- **GraphQL integration**: For data fetching
- **WebAssembly support**: Alternative compilation target

---

**📞 Questions or Suggestions?**

This roadmap is a living document. We welcome feedback and suggestions from the community:

- **GitHub Discussions**: For general roadmap discussion
- **GitHub Issues**: For specific feature requests
- **Discord/Slack**: For real-time community input

Let's build the future of Stacks development together! 🚀
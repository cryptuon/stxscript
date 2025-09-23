"""
StxScript Project Scaffolding
Creates new StxScript projects with templates and best practices
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ProjectTemplate:
    """Base class for project templates"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def create_structure(self, project_path: Path, context: Dict[str, Any]) -> None:
        """Create the project directory structure"""
        raise NotImplementedError

    def generate_files(self, project_path: Path, context: Dict[str, Any]) -> None:
        """Generate template files"""
        raise NotImplementedError


class BasicTemplate(ProjectTemplate):
    """Basic StxScript project template"""

    def __init__(self):
        super().__init__(
            name="basic",
            description="Basic StxScript smart contract template"
        )

    def create_structure(self, project_path: Path, context: Dict[str, Any]) -> None:
        """Create basic project structure"""
        directories = [
            "src",
            "tests",
            "docs",
            "scripts",
            "contracts"  # For compiled Clarity contracts
        ]

        for directory in directories:
            (project_path / directory).mkdir(parents=True, exist_ok=True)

    def generate_files(self, project_path: Path, context: Dict[str, Any]) -> None:
        """Generate basic template files"""
        project_name = context["project_name"]

        # Create main contract file
        main_contract = f"""// {project_name} - Basic StxScript Contract
// Generated on {datetime.now().strftime('%Y-%m-%d')}

// Contract definition
const CONTRACT_NAME: string = "{project_name}";

// Data variables
let counter: uint = 0u;
let owner: principal = tx-sender;

// Public functions
function increment(): uint {{
    counter = counter + 1u;
    return counter;
}}

function get_counter(): uint {{
    return counter;
}}

function set_counter(value: uint): uint {{
    // Only owner can set counter
    if (tx-sender != owner) {{
        return err(u"ERR_UNAUTHORIZED");
    }}
    counter = value;
    return counter;
}}

// Read-only functions
function get_owner(): principal {{
    return owner;
}}
"""
        (project_path / "src" / "main.stx").write_text(main_contract)

        # Create package.json equivalent
        project_config = {
            "name": project_name,
            "version": "1.0.0",
            "description": f"StxScript smart contract: {project_name}",
            "main": "src/main.stx",
            "scripts": {
                "build": "stxscript build src/main.stx contracts/main.clar",
                "check": "stxscript check src/",
                "format": "stxscript fmt src/",
                "lint": "stxscript lint src/",
                "test": "clarinet test",
                "deploy": "clarinet deploy"
            },
            "stxscript": {
                "version": "0.1.0",
                "target": "clarity-2"
            }
        }

        with open(project_path / "stx-project.json", 'w') as f:
            json.dump(project_config, f, indent=2)

        # Create README
        readme_content = f"""# {project_name}

A StxScript smart contract for Stacks blockchain.

## Overview

This project demonstrates basic StxScript functionality including:
- Data variables and state management
- Public and read-only functions
- Access control patterns
- Error handling

## Getting Started

### Prerequisites

- StxScript compiler (`stxscript`)
- Clarinet (for testing and deployment)

### Building

```bash
# Compile to Clarity
npm run build
# or
stxscript build src/main.stx contracts/main.clar
```

### Testing

```bash
# Check syntax
npm run check

# Format code
npm run format

# Lint code
npm run lint

# Run tests (requires Clarinet)
npm run test
```

### Project Structure

```
{project_name}/
├── src/              # StxScript source files
│   └── main.stx      # Main contract
├── contracts/        # Compiled Clarity contracts
├── tests/           # Test files
├── docs/            # Documentation
├── scripts/         # Build and deployment scripts
└── stx-project.json # Project configuration
```

## Usage

The contract provides a simple counter that can be incremented and managed:

```stxscript
// Increment the counter
let result = increment();

// Get current counter value
let value = get_counter();

// Set counter (owner only)
let new_value = set_counter(42u);
```

## Development

This project follows StxScript best practices:

- Clear function signatures with types
- Proper error handling
- Access control patterns
- Comprehensive documentation

For more information about StxScript, visit the [official documentation](https://github.com/cryptuon/stxscript).

## License

MIT License
"""
        (project_path / "README.md").write_text(readme_content)

        # Create basic test file
        test_content = f"""// Tests for {project_name}
// StxScript test file

import {{ assertEquals, assertError }} from "std/testing";
import {{ {project_name.replace('-', '_')} }} from "../src/main.stx";

// Test basic functionality
test("counter starts at zero", () => {{
    let initial = get_counter();
    assertEquals(initial, 0u);
}});

test("increment increases counter", () => {{
    let before = get_counter();
    increment();
    let after = get_counter();
    assertEquals(after, before + 1u);
}});

test("set_counter works for owner", () => {{
    let result = set_counter(42u);
    assertEquals(result, 42u);
    assertEquals(get_counter(), 42u);
}});

test("unauthorized access fails", () => {{
    // TODO: Test with different tx-sender
    // This would require Clarinet testing framework
}});
"""
        (project_path / "tests" / "main.test.stx").write_text(test_content)

        # Create .gitignore
        gitignore_content = """# Build outputs
contracts/
*.clar

# Dependencies
node_modules/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# StxScript
.stxscript/
"""
        (project_path / ".gitignore").write_text(gitignore_content)


class NFTTemplate(ProjectTemplate):
    """NFT contract template"""

    def __init__(self):
        super().__init__(
            name="nft",
            description="Non-Fungible Token (NFT) contract template"
        )

    def create_structure(self, project_path: Path, context: Dict[str, Any]) -> None:
        """Create NFT project structure"""
        directories = [
            "src",
            "tests",
            "assets",
            "metadata",
            "contracts"
        ]

        for directory in directories:
            (project_path / directory).mkdir(parents=True, exist_ok=True)

    def generate_files(self, project_path: Path, context: Dict[str, Any]) -> None:
        """Generate NFT template files"""
        project_name = context["project_name"]

        nft_contract = f"""// {project_name} NFT Contract
// SIP-009 compliant Non-Fungible Token

// Constants
const CONTRACT_OWNER: principal = tx-sender;
const ERR_OWNER_ONLY: uint = u100;
const ERR_NOT_TOKEN_OWNER: uint = u101;
const ERR_TOKEN_NOT_FOUND: uint = u102;

// Data variables
let last_token_id: uint = 0u;

// Data maps
map token_owners principal uint;  // token-id -> owner
map token_metadata uint {{
    name: string,
    description: string,
    image: string
}};

// Token metadata
const TOKEN_NAME: string = "{project_name} NFT";
const TOKEN_SYMBOL: string = "NFT";

// SIP-009 Functions
function get_owner(token_id: uint): principal {{
    return token_owners.get(token_id);
}}

function get_token_uri(token_id: uint): string {{
    let metadata = token_metadata.get(token_id);
    return metadata.image;
}}

function transfer(token_id: uint, sender: principal, recipient: principal): boolean {{
    let owner = token_owners.get(token_id);

    if (owner != sender) {{
        return err(ERR_NOT_TOKEN_OWNER);
    }}

    token_owners.set(token_id, recipient);
    return ok(true);
}}

// Minting function
function mint(recipient: principal, name: string, description: string, image: string): uint {{
    if (tx-sender != CONTRACT_OWNER) {{
        return err(ERR_OWNER_ONLY);
    }}

    last_token_id = last_token_id + 1u;
    let token_id = last_token_id;

    token_owners.set(token_id, recipient);
    token_metadata.set(token_id, {{
        name: name,
        description: description,
        image: image
    }});

    return ok(token_id);
}}

// Read-only functions
function get_last_token_id(): uint {{
    return last_token_id;
}}

function get_token_metadata(token_id: uint): object {{
    return token_metadata.get(token_id);
}}
"""
        (project_path / "src" / "nft.stx").write_text(nft_contract)


class TokenTemplate(ProjectTemplate):
    """Fungible token template"""

    def __init__(self):
        super().__init__(
            name="token",
            description="Fungible Token (SIP-010) contract template"
        )

    def create_structure(self, project_path: Path, context: Dict[str, Any]) -> None:
        """Create token project structure"""
        directories = [
            "src",
            "tests",
            "docs",
            "contracts"
        ]

        for directory in directories:
            (project_path / directory).mkdir(parents=True, exist_ok=True)

    def generate_files(self, project_path: Path, context: Dict[str, Any]) -> None:
        """Generate token template files"""
        project_name = context["project_name"]

        token_contract = f"""// {project_name} Token Contract
// SIP-010 compliant Fungible Token

// Token constants
const TOKEN_NAME: string = "{project_name} Token";
const TOKEN_SYMBOL: string = "TKN";
const TOKEN_DECIMALS: uint = 6u;
const TOTAL_SUPPLY: uint = 1000000000000u; // 1M tokens with 6 decimals

// Error constants
const ERR_INSUFFICIENT_BALANCE: uint = u1;
const ERR_UNAUTHORIZED: uint = u2;

// Data variables
let contract_owner: principal = tx-sender;

// Token balances
map balances principal uint;

// Initialize contract
function initialize(): boolean {{
    balances.set(contract_owner, TOTAL_SUPPLY);
    return ok(true);
}}

// SIP-010 Functions
function transfer(amount: uint, sender: principal, recipient: principal, memo: buffer): boolean {{
    let sender_balance = balances.get(sender);

    if (sender_balance < amount) {{
        return err(ERR_INSUFFICIENT_BALANCE);
    }}

    balances.set(sender, sender_balance - amount);
    let recipient_balance = balances.get(recipient);
    balances.set(recipient, recipient_balance + amount);

    return ok(true);
}}

function get_name(): string {{
    return TOKEN_NAME;
}}

function get_symbol(): string {{
    return TOKEN_SYMBOL;
}}

function get_decimals(): uint {{
    return TOKEN_DECIMALS;
}}

function get_balance(account: principal): uint {{
    return balances.get(account);
}}

function get_total_supply(): uint {{
    return TOTAL_SUPPLY;
}}

// Additional functions
function mint(recipient: principal, amount: uint): boolean {{
    if (tx-sender != contract_owner) {{
        return err(ERR_UNAUTHORIZED);
    }}

    let current_balance = balances.get(recipient);
    balances.set(recipient, current_balance + amount);

    return ok(true);
}}
"""
        (project_path / "src" / "token.stx").write_text(token_contract)


class DeFiTemplate(ProjectTemplate):
    """DeFi protocol template"""

    def __init__(self):
        super().__init__(
            name="defi",
            description="DeFi protocol template with basic AMM functionality"
        )

    def create_structure(self, project_path: Path, context: Dict[str, Any]) -> None:
        """Create DeFi project structure"""
        directories = [
            "src",
            "tests",
            "docs",
            "contracts"
        ]

        for directory in directories:
            (project_path / directory).mkdir(parents=True, exist_ok=True)

    def generate_files(self, project_path: Path, context: Dict[str, Any]) -> None:
        """Generate DeFi template files"""
        project_name = context["project_name"]

        defi_contract = f"""// {project_name} DeFi Protocol
// Basic AMM (Automated Market Maker) implementation

// Constants
const CONTRACT_OWNER: principal = tx-sender;
const FEE_RATE: uint = 30u; // 0.3% fee (30 basis points)
const FEE_DENOMINATOR: uint = 10000u;

// Error codes
const ERR_UNAUTHORIZED: uint = u100;
const ERR_INSUFFICIENT_LIQUIDITY: uint = u101;
const ERR_INSUFFICIENT_BALANCE: uint = u102;
const ERR_SLIPPAGE_EXCEEDED: uint = u103;

// Pool state
let total_token_a: uint = 0u;
let total_token_b: uint = 0u;
let total_shares: uint = 0u;

// User liquidity shares
map liquidity_shares principal uint;

// Liquidity provision
function add_liquidity(token_a_amount: uint, token_b_amount: uint): uint {{
    let shares_to_mint: uint;

    if (total_shares == 0u) {{
        // Initial liquidity
        shares_to_mint = sqrt(token_a_amount * token_b_amount);
    }} else {{
        // Proportional liquidity
        let share_a = (token_a_amount * total_shares) / total_token_a;
        let share_b = (token_b_amount * total_shares) / total_token_b;
        shares_to_mint = min(share_a, share_b);
    }}

    total_token_a = total_token_a + token_a_amount;
    total_token_b = total_token_b + token_b_amount;
    total_shares = total_shares + shares_to_mint;

    let current_shares = liquidity_shares.get(tx-sender);
    liquidity_shares.set(tx-sender, current_shares + shares_to_mint);

    return ok(shares_to_mint);
}}

function remove_liquidity(shares: uint): object {{
    let user_shares = liquidity_shares.get(tx-sender);

    if (user_shares < shares) {{
        return err(ERR_INSUFFICIENT_BALANCE);
    }}

    let token_a_amount = (shares * total_token_a) / total_shares;
    let token_b_amount = (shares * total_token_b) / total_shares;

    total_token_a = total_token_a - token_a_amount;
    total_token_b = total_token_b - token_b_amount;
    total_shares = total_shares - shares;

    liquidity_shares.set(tx-sender, user_shares - shares);

    return ok({{
        token_a: token_a_amount,
        token_b: token_b_amount
    }});
}}

// Token swapping
function swap_a_to_b(token_a_in: uint, min_token_b_out: uint): uint {{
    if (total_token_a == 0u || total_token_b == 0u) {{
        return err(ERR_INSUFFICIENT_LIQUIDITY);
    }}

    // Calculate output using constant product formula (x * y = k)
    let token_a_in_with_fee = token_a_in * (FEE_DENOMINATOR - FEE_RATE);
    let numerator = token_a_in_with_fee * total_token_b;
    let denominator = (total_token_a * FEE_DENOMINATOR) + token_a_in_with_fee;
    let token_b_out = numerator / denominator;

    if (token_b_out < min_token_b_out) {{
        return err(ERR_SLIPPAGE_EXCEEDED);
    }}

    total_token_a = total_token_a + token_a_in;
    total_token_b = total_token_b - token_b_out;

    return ok(token_b_out);
}}

function swap_b_to_a(token_b_in: uint, min_token_a_out: uint): uint {{
    if (total_token_a == 0u || total_token_b == 0u) {{
        return err(ERR_INSUFFICIENT_LIQUIDITY);
    }}

    let token_b_in_with_fee = token_b_in * (FEE_DENOMINATOR - FEE_RATE);
    let numerator = token_b_in_with_fee * total_token_a;
    let denominator = (total_token_b * FEE_DENOMINATOR) + token_b_in_with_fee;
    let token_a_out = numerator / denominator;

    if (token_a_out < min_token_a_out) {{
        return err(ERR_SLIPPAGE_EXCEEDED);
    }}

    total_token_b = total_token_b + token_b_in;
    total_token_a = total_token_a - token_a_out;

    return ok(token_a_out);
}}

// Read-only functions
function get_pool_info(): object {{
    return {{
        token_a_reserve: total_token_a,
        token_b_reserve: total_token_b,
        total_shares: total_shares
    }};
}}

function get_user_shares(user: principal): uint {{
    return liquidity_shares.get(user);
}}

// Helper functions
function min(a: uint, b: uint): uint {{
    if (a < b) {{
        return a;
    }} else {{
        return b;
    }}
}}

function sqrt(n: uint): uint {{
    // Simplified square root implementation
    if (n == 0u) {{
        return 0u;
    }}

    let x = n;
    let y = (x + 1u) / 2u;

    while (y < x) {{
        x = y;
        y = (x + n / x) / 2u;
    }}

    return x;
}}
"""
        (project_path / "src" / "defi.stx").write_text(defi_contract)


# Template registry
TEMPLATES = {
    "basic": BasicTemplate(),
    "nft": NFTTemplate(),
    "token": TokenTemplate(),
    "defi": DeFiTemplate()
}


def create_project(project_path: Path, template_name: str = "basic", verbose: bool = False) -> None:
    """Create a new StxScript project using the specified template"""

    if template_name not in TEMPLATES:
        raise ValueError(f"Unknown template: {template_name}. Available: {', '.join(TEMPLATES.keys())}")

    template = TEMPLATES[template_name]
    project_name = project_path.name

    if verbose:
        print(f"Creating {template.description}...")

    # Create project context
    context = {
        "project_name": project_name,
        "template_name": template_name,
        "creation_date": datetime.now().isoformat(),
    }

    # Create directory structure
    project_path.mkdir(parents=True, exist_ok=True)
    template.create_structure(project_path, context)

    if verbose:
        print("✅ Created directory structure")

    # Generate template files
    template.generate_files(project_path, context)

    if verbose:
        print("✅ Generated template files")
        print(f"📁 Project structure:")
        _print_directory_tree(project_path)


def _print_directory_tree(path: Path, prefix: str = "", max_depth: int = 3, current_depth: int = 0) -> None:
    """Print directory tree structure"""
    if current_depth >= max_depth:
        return

    items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))

    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        print(f"{prefix}{current_prefix}{item.name}")

        if item.is_dir() and not item.name.startswith('.'):
            next_prefix = prefix + ("    " if is_last else "│   ")
            _print_directory_tree(item, next_prefix, max_depth, current_depth + 1)


def list_templates() -> Dict[str, str]:
    """List available project templates"""
    return {name: template.description for name, template in TEMPLATES.items()}


if __name__ == "__main__":
    # Example usage
    test_project = Path("test-project")
    create_project(test_project, "basic", verbose=True)
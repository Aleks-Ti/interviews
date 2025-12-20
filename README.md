# Development

Your new bare-bones project includes minimal organization with a single `main.rs` file and a few assets.

```bash
project/
├─ assets/ # Any assets that are used by the app should be placed here
├─ src/
│  ├─ main.rs # main.rs is the entry point to your application and currently contains all components for the app
├─ Cargo.toml # The Cargo.toml file defines the dependencies and feature flags for your project
```

## Навигация

- [инструменты](#инструменты)
- - [wasm32](#wasm32)
- - [dioxus](#dioxus)
- - - [base dioxus](#base-dioxus)

## Инструменты

### wasm32

```bash
rustup target add wasm32-unknown-unknown
```

### dioxus

```bash
cargo install cargo-binstall
```

and

```bash
cargo install dioxus-cli
```

#### base dioxus

- Запуск:

```bash
dx serve
```

Run the following command in the root of your project to start developing with the default platform:

```bash
dx serve
```

To run for a different platform, use the `--platform platform` flag. E.g.

```bash
dx serve --platform desktop
```

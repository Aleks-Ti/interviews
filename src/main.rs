mod dto;
use dioxus::prelude::*;

const FAVICON: Asset = asset!("/assets/diploma_icon_262691.ico");
const MAIN_CSS: Asset = asset!("/assets/main.css");
const HEADER_SVG: Asset = asset!("/assets/diploma_icon_262691.svg");

fn main() {
    dioxus::launch(App);
}

#[component]
fn App() -> Element {
    rsx! {
        document::Link { rel: "icon", href: FAVICON }
        document::Link { rel: "stylesheet", href: MAIN_CSS }
        Header { name: "Interview APP" }
        MainContent {}
        Footer {}
    }
}

#[component]
pub fn Header(name: String) -> Element {
    rsx! {
        div {
            id: "header",
            img { src: HEADER_SVG, id: "header" , width: "80", height: "50"}
            div { id: "links",
                h2 { "This is {name}" }
            }
        }
    }
}

async fn fetch_backend_plans() -> Vec<String> {
    vec!["qwer".to_string(), "QWEr".to_string()]
}

#[component]
fn PlansList() -> Element {
    let plans = use_resource(|| async { fetch_backend_plans().await });
    let mut refreshed = use_signal(|| 0); // счётчик обновлений

    rsx! {
        div {
            button {
                onclick: move |_| refreshed += 1,
                "Обновить ({refreshed})"
            }
            div {
                match plans() {
                    None => rsx! { "Загрузка..." },
                    Some(plans) => rsx! {
                        if plans.is_empty() {
                            "Нет планов"
                        } else {
                            ul {
                                for plan in plans.iter() {
                                    li { "{plan}" }
                                }
                            }
                        }
                    },
                }
            }
        }
    }
}

#[component]
fn MainContent() -> Element {
    rsx! {
        div {
            id: "links",
            h2 { "This is name" }
            PlansList {}
        }
    }
}

#[component]
pub fn Footer() -> Element {
    rsx! {
        div {
            id: "footer",
            img { src: HEADER_SVG, id: "header" , width: "80", height: "50"}
        }
    }
}

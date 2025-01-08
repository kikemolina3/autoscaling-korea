use actix_web::{web, App, HttpServer, HttpResponse};
use serde::{Deserialize, Serialize};
use futures::future::join_all;

#[derive(Serialize, Deserialize)]
struct User {
    name: String,
    age: u32,
}

// Endpoint que devuelve una respuesta JSON con información del usuario
async fn get_user() -> HttpResponse {
    let user = User {
        name: "Alice".to_string(),
        age: 30,
    };
    HttpResponse::Ok().json(user)
}

// Función que simula tareas asíncronas
async fn simulate_task(id: u32) {
    tokio::time::sleep(std::time::Duration::from_secs(2)).await;
    println!("Task {} completed", id);
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // Crear servidor web
    HttpServer::new(|| {
        App::new()
            .route("/", web::get().to(|| async { HttpResponse::Ok().body("Hello, World!") }))
            .route("/user", web::get().to(get_user))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}

from fastapi import FastAPI

from src.config.db_setup import Base, engine
from src.routers import auth_router, admin_router, category_router, product_router, user_router, cart_router, order_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title="🛍️ E-Commerce API", description=("Welcome to the **E-Commerce API**! 🚀\n\n"
                                                      "This API powers a full-featured e-commerce platform, providing:\n"
                                                      "- 🛒 **Product Management**: Add, update, and manage products.\n"
                                                      "- 🔒 **User Authentication**: Secure login and registration.\n"
                                                      "- 🛍️ **Shopping Cart**: Manage your items effortlessly.\n"
                                                      "- 📦 **Order Processing**: Track and fulfill orders.\n"
                                                      "- 💳 **Payments**: Integration with payment gateways.\n\n"
                                                      "Build amazing e-commerce experiences with ease! 🌟"),
              version="1.0.0", terms_of_service="https://yourwebsite.com/terms",
              contact={"name": "Support Team", "url": "https://yourwebsite.com/support",
                       "email": "support@yourwebsite.com", },
              license_info={"name": "MIT License", "url": "https://opensource.org/licenses/MIT"},
              docs_url="/docs",
              redoc_url="/redoc",
              openapi_url="/openapi.json",
              )

app.include_router(auth_router.auth_routes)
app.include_router(admin_router.admin_routes)
app.include_router(category_router.category_routes)
app.include_router(product_router.product_routes)
app.include_router(user_router.user_routes)
app.include_router(cart_router.cart_routes)
app.include_router(order_router.order_routes)

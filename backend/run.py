#!/usr/bin/env python
from app import create_app
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

if __name__ == '__main__':
    app = create_app()
    logger.info("启动Flask应用...")
    app.run(host='0.0.0.0', port=5000, debug=False)

from router.app_router import AppRouter

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(AppRouter.instance(), host='0.0.0.0', port=9000, workers=1)

from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(
    max_workers=2,
    thread_name_prefix="vertigo-bg"
)
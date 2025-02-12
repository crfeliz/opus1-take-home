def find_item_by_id(collection, item_id):
    return next((item for item in collection if item.id == item_id), None)


def edit_item_by_id(collection, item_id, f):
    f(find_item_by_id(collection, item_id))


def remove_item_by_id(collection, item_id):
    item_to_remove = find_item_by_id(collection, item_id)
    if item_to_remove is None:
        raise ValueError(f"Item with ID {item_id} not found in collection {collection}")
    collection.remove(item_to_remove)


def with_item_moved_by_id(collection, item_id, new_index):
    item_index = next((i for i, item in enumerate(collection) if item.id == item_id), None)
    if item_index is None:
        raise ValueError(f"Item {item_id} not found in {collection}")

    item = collection[item_index]
    collection[item_index] = None
    collection.insert(new_index, item)
    return list(filter(None, collection))

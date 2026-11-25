# Searchable

Bind `searchable(text:)` to local state. Add `searchScopes` when modes such as messages and people change which results a query can return.

```swift
.searchable(text: $searchQuery, prompt: Text("Search"))
.searchScopes($searchScope) {
  ForEach(SearchScope.allCases, id: \.self) { scope in
    Text(scope.title).tag(scope)
  }
}
```

Follow [async state and task lifecycle](../../../shared/swiftui/async-state.md) for debouncing, cancellation, and error states. Key the task by both query and scope so switching modes starts the matching search. Capture that request before awaiting, then check that the task is still active before publishing its result.

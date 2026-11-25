# SwiftUI Async State

Use `.task` for view-owned work that can stop when the view disappears. Use `.task(id:)` when a changed input must restart the work. Give a service or model ownership of work that must survive the view.

Capture the input before suspension. Check cancellation again after a fetch, since services may return even after the task is cancelled. Treat an empty result as data and show a separate error state when a request fails.

```swift
@MainActor
struct SearchView: View {
  enum SearchState {
    case idle, loading, results([SearchResult]), failed
  }

  @Environment(SearchClient.self) private var client
  @State private var query = ""
  @State private var state: SearchState = .idle

  var body: some View {
    List {
      switch state {
      case .idle:
        Text("Enter a search term")
      case .loading:
        ProgressView()
      case .results(let items):
        if items.isEmpty {
          Text("No results")
        } else {
          ForEach(items) { item in
            Text(item.title)
          }
        }
      case .failed:
        Text("Search failed")
      }
    }
    .searchable(text: $query)
    .task(id: query) { [query] in
      await search(query)
    }
  }

  private func search(_ requestedQuery: String) async {
    guard !Task.isCancelled, query == requestedQuery else { return }
    guard !requestedQuery.isEmpty else {
      state = .idle
      return
    }

    state = .loading
    do {
      try await Task.sleep(for: .milliseconds(250))
      let items = try await client.search(requestedQuery)
      guard !Task.isCancelled, query == requestedQuery else { return }
      state = .results(items)
    } catch is CancellationError {
      return
    } catch {
      guard !Task.isCancelled, query == requestedQuery else { return }
      state = .failed
    }
  }
}
```

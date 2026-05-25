# 49. Network Manager & Social Graph

## 1. Abstract: Auditing the Developer Graph
GitHub is not merely a code hosting platform; it is the premier social network for developers. Managing connections, tracking influential follows, and auditing network reciprocity are often tedious manual tasks. The Graphite-Git Network Manager automates this process. This document details the algorithmic logic used to traverse the social graph, identify non-reciprocal follows, and implement defensive features like the "Safety Net" whitelist.

## 2. The Value of the Social Graph
In the open-source ecosystem, a developer's network is their distribution channel. Followers amplify project visibility. However, follow-for-follow spam and network bloat are common. The Network Manager provides surgical tools to prune and maintain a high-quality, reciprocal social graph.

## 3. Data Retrieval and Algorithmic Intersection

To determine reciprocity, the system must fetch and compare two distinct datasets: the users you follow, and the users who follow you.

### 3.1 Pagination and Data Ingestion
The `/user/followers` and `/user/following` endpoints are paginated. A recursive or loop-based fetching mechanism in `githubService` must exhaust all pages to build complete arrays of `User` objects. For accounts with massive followings, this process displays a deterministic progress bar to the user.

### 3.2 The Intersection Algorithm
Once both arrays are complete, a set-based algorithm determines reciprocity.
Using JavaScript `Set` objects provides $O(1)$ lookup times, drastically speeding up the comparison compared to nested array loops.

```javascript
// Conceptual Algorithm
const followersSet = new Set(followersArray.map(u => u.login));
const followingSet = new Set(followingArray.map(u => u.login));

const nonReciprocalFollows = followingArray.filter(u => !followersSet.has(u.login));
const fans = followersArray.filter(u => !followingSet.has(u.login));
```

## 4. The "Safety Net" Whitelist

Blindly unfollowing all non-reciprocal connections is dangerous. A developer may follow Linus Torvalds or a major organization without expecting a follow back.

### 4.1 Implementation
The "Safety Net" is a local-only whitelist. It is an array of usernames stored in the browser's `localStorage` (e.g., `graphite_safety_net: ['torvalds', 'microsoft']`).
Before presenting the `nonReciprocalFollows` list to the user for potential unfollowing, the array is filtered against the Safety Net.

### 4.2 UI Integration
In the Network Manager UI, every user card features a "Shield" icon. Clicking this icon adds/removes the user from the local Safety Net array. Whitelisted users are entirely hidden from the "Audit" view, ensuring they are never accidentally unfollowed during a mass prune.

```mermaid
graph TD
    A[Fetch Following] --> B(Complete Following List)
    C[Fetch Followers] --> D(Complete Followers List)
    
    B --> E{Intersection Engine}
    D --> E
    
    E --> F[Raw Non-Reciprocal List]
    
    G[(LocalStorage: Safety Net)] --> H{Filter Engine}
    F --> H
    
    H --> I[Safe Audit List for UI]
    I --> J[User Executes Unfollow]
    J --> K[GitHub API: DELETE /user/following/{username}]
```

## 5. Bulk Operations and API Throttling

When a user decides to unfollow multiple non-reciprocal accounts, they can trigger a bulk operation.
- **The Danger of Rapid Mutation:** Firing 50 `DELETE` requests simultaneously will trigger GitHub's abuse detection mechanisms, potentially resulting in a temporary API ban.
- **The Throttler:** The UI queues the unfollow actions and executes them sequentially with a deliberate delay (e.g., 500ms to 1000ms between requests), displaying a live progress indicator to the user.

## 6. Future Expansion: Graph Visualization

The next phase of the Network Manager roadmap involves visualizing the social graph. By utilizing libraries like D3.js or React Flow, the application will render a web of connections, allowing developers to visually identify clusters of influence, shared connections, and central nodes within their specific open-source niche.

## 7. Conclusion

The Network Manager treats the social aspect of GitHub with the same rigorous engineering logic as the codebase itself. By providing powerful intersection algorithms, protective whitelists, and rate-limited bulk operations, Graphite-Git empowers developers to curate a high-signal, professional network, free from spam and asymmetrical relationships.

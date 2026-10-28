# Navigation review — 27 October 2026

## Changes

- Default composition filters, page 1 and six items per page are omitted from
  URLs. Changed values remain shareable: `/compositions?q=Chopin`,
  `/compositions?p=2` and `/compositions?size=12`.
- A canonical history entry records that its empty query is intentional. Back,
  Forward and reload can restore the default selection even if session storage
  was updated later. A fresh menu visit still restores the account's tab session.
- Library query changes retain the mounted page. Previously its error-boundary
  key recreated the search input after each character. Ordinary sequential
  typing lost focus; bulk fill testing had missed this. Pagination also lost
  its list reference before the scheduled scroll. Both are fixed.
- Page and page-size changes scroll to the first result, honoring reduced motion.
- Sidebar and logo destinations are native links. Ordinary clicks retain SPA
  navigation; modified and auxiliary clicks retain browser behavior. The logo
  links to the authenticated studio, matching its ordinary-click destination.

## Browser evidence

Chrome review used the live composition/detail pages and a disposable local
account for exercises and study pages, protecting the owner's learning progress.
Sequential `Chopin` typing was reproduced failing before the routing fix and
completed afterward with the search field still focused. Page 2 used only `p=2`,
Back restored bare `/compositions`, and changing to 12 items used only `size=12`.
After pagination the first result was visible below the fixed header.

## Further navigation improvements

1. **Remember the route into the full player.** Opening a player directly from
   the library and pressing Back currently opens composition lessons. Returning
   to the filtered library takes another step. A contextual return destination
   should keep a safe parent fallback for direct/new-tab visits.
2. **Persist exercise and theory filters.** Searching `Besh`, opening an exercise
   and returning to the exercise list loses the search. These libraries should
   adopt the same URL/session behavior as compositions. Theory shares this view.
3. **Keep the position when returning to long lists.** Returning from a detail
   page currently starts at the list heading. Restoring the original card and
   scroll position would help on later pages and on mobile.
4. **Make composition titles detail links.** The title is currently plain text;
   only the separate Lessons action opens its detail page. A title link would
   offer a larger, predictable target without making preview/favorite clicks
   navigate accidentally.

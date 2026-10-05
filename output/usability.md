# Campus Customs Usability Improvements

Usability improvements should solve shopper problems that make the experience less positive. The goal is to make finding target items extremely easy and create a seamless, positive experience from browsing to chatting with the shop assistant.

The site should be clean, organized, easy to read, and easy to navigate. The agent and backend should answer questions quickly and accurately, prevent incorrect information, protect customer data, and avoid creating confusion. Improvements should help both the shopper and the Campus Customs business.

## Improvements added

### 1. Product category filter

What I added: The Products page now has a working category filter for items such as hoodies, crewnecks, T-shirts, jackets, and quarter-zips. The shopper can use the category filter together with the search box.

Why it helps the shopper: It makes finding a target type of item much easier. A shopper who wants a hoodie does not have to scan through every product, which makes browsing faster and less frustrating.

Why it helps Campus Customs: Clearer product organization can help shoppers discover products more quickly and may make them more likely to find something they want to purchase.

### 2. Clear empty-search results

What I added: When a search and category combination does not return products, the page shows a clear message telling the shopper that there are no matches and suggesting that they try another search or category.

Why it helps the shopper: A blank page can feel like the site is broken. The message explains what happened and gives the shopper an obvious next step, so the experience remains clear and positive.

Why it helps Campus Customs: Clear feedback reduces confusion and prevents shoppers from abandoning the site because they think the catalogue failed to load.

### 3. Quick chat prompts

What I added: The chat panel offers starter prompts such as “Show me hoodies” and “What’s in stock?”

Why it helps the shopper: Shoppers do not have to figure out the perfect wording before using the assistant. They can start quickly and see the kinds of questions the agent can answer.

Why it helps Campus Customs: Quick prompts encourage more shoppers to use the assistant, which can make product discovery and support more efficient.

### 4. More natural catalogue search

What I added: The backend search removes conversational filler words and recognizes natural requests such as “What hoodies do y’all have?” instead of requiring a short, database-style query.

Why it helps the shopper: The shopper can speak naturally and still receive relevant products. This makes the assistant feel more personal and seamless.

Why it helps Campus Customs: Better search accuracy means fewer missed product matches and fewer follow-up questions caused by the agent failing to understand a normal request.

### 5. Validation for blank chat messages

What I added: The backend rejects blank or whitespace-only chat messages before sending them to the agent, and the frontend shows a readable error when the assistant cannot respond.

Why it helps the shopper: The user receives clear feedback instead of a confusing failure or an empty response.

Why it helps Campus Customs: Validation avoids wasting model calls on unusable requests, improves reliability, and can reduce unnecessary API costs.

## Standards for future improvements

Every new improvement should be checked against these questions:

- Does it solve a real shopper problem?
- Does it make target products easier to find?
- Is the site clean, organized, readable, and easy to navigate?
- Does it make the experience feel seamless, positive, and personal?
- Does the agent answer quickly, accurately, and safely?
- Does it prevent wrong information or confusing responses?
- Does it help Campus Customs reduce support friction, improve product discovery, or operate more efficiently?

## Improvements that would make the experience stronger

### Loading and connection feedback

The chat and catalogue should show clear loading states when waiting for the backend. If the backend is unavailable, the site should explain what happened and let the shopper try again. This keeps the experience understandable during slow connections or temporary failures.

### Better accessibility

The site should continue improving keyboard navigation, focus states, color contrast, image alt text, and screen-reader labels. A clean design should be easy for as many campus shoppers as possible to use.

### Helpful product filters

Price range, color, and in-stock-only filters would make it even easier to narrow a large catalogue. These filters should use real catalogue and inventory data so they do not create misleading results.

### Agent response grounding

The agent should continue calling the database tools before answering about prices, colors, sizes, or stock. It should clearly say when an item or size is unavailable instead of guessing. This protects customer trust and prevents incorrect shopping information.

### Personal but privacy-conscious assistance

Logged-in shoppers can receive personalized help based on their conversation history, but the agent should not expose passwords, credentials, or unnecessary account details. Personalization should make the experience feel thoughtful without making the shopper feel watched or confused.

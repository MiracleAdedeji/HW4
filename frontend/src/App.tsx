import { FormEvent, useEffect, useState } from 'react'
import { ArrowRight, Bot, Search, Send, ShoppingBag, Sparkles, X } from 'lucide-react'
import catalogue from './catalogue.json'

const API_BASE_URL = ''

type Product = { product_id: string; name: string; garment_type: string; price: number; description: string; image_file_path: string; search_tags?: string[]; colors?: string[]; inventory?: { size: string; quantity: number }[] }

function ProductGrid({ query = '', category = 'All', items }: { query?: string; category?: string; items?: Product[] }) {
  const source: Product[] = items || (catalogue as unknown as Product[])
  const normalizeSearch = (value: string) => value.toLowerCase().replace(/\bvs\.?\b/g, 'v').replace(/[^a-z0-9]+/g, ' ').trim()
  const normalizedQuery = normalizeSearch(query)
  const queryWords = normalizedQuery.split(/\s+/).filter((word) => word.length > 1 && !['a', 'an', 'the', 'do', 'does', 'is', 'are', 'what', 'which', 'have', 'has', 'you', 'your', 'all', 'of', 'for', 'me', 'show'].includes(word))
  const visible = source.filter((p) => {
    const matchesCategory = category === 'All' || p.garment_type.toLowerCase().includes(category.toLowerCase())
    const searchable = normalizeSearch(`${p.name} ${p.garment_type} ${p.description} ${p.search_tags?.join(' ') || ''}`)
    const matchesQuery = !normalizedQuery || searchable.includes(normalizedQuery) || queryWords.every((word) => searchable.includes(word))
    return matchesCategory && matchesQuery
  })
  return <>{visible.length > 0 ? <div className="product-grid">{visible.map((p) => <a className="product-card" href={`#product/${p.product_id}`} key={p.product_id}><div className="product-image"><img src={`/${p.image_file_path}`} alt={p.name} /></div><div className="product-info"><div><h3>{p.name}</h3><p>{p.garment_type} · {p.description.slice(0, 58)}{p.description.length > 58 ? '…' : ''}</p></div><strong>${p.price.toFixed(2)}</strong></div></a>)}</div> : <div className="empty-results"><h3>No matches yet.</h3><p>Try another search or category, and we’ll keep looking.</p></div>}</>
}

function ProductDetail({ productId }: { productId: string }) {
  const product = catalogue.find((item) => item.product_id === productId)
  if (!product) return <section className="empty-page"><h1>Product not found.</h1><a className="button pink" href="#products">Back to products</a></section>
  const totalStock = product.inventory.reduce((total, item) => total + item.quantity, 0)
  return <section className="detail-page"><a className="back-link" href="#products">← Back to products</a><div className="detail-layout"><div className="detail-image"><img src={`/${product.image_file_path}`} alt={product.name} /></div><div className="detail-copy"><p className="eyebrow">{product.garment_type}</p><h1>{product.name}</h1><p className="detail-price">${product.price.toFixed(2)}</p><p className="detail-description">{product.description}</p><div className="detail-colors"><strong>Colors</strong><span>{product.colors.join(' · ')}</span></div>{product.inventory.length > 0 && <div className="stock-block"><div className="stock-heading"><strong>Size & availability</strong><span>{totalStock > 0 ? `${totalStock} in stock` : 'Out of stock'}</span></div><div className="size-list">{product.inventory.map((item) => <div key={item.size}><span>{item.size}</span><span className={item.quantity === 0 ? 'out' : ''}>{item.quantity > 0 ? `${item.quantity} available` : 'Sold out'}</span></div>)}</div></div>}<button className="button pink" disabled={totalStock === 0}>Add to bag <ShoppingBag size={16} /></button></div></div></section>
}

function Home() {
  return <><section className="hero" id="home"><div className="hero-copy"><p className="eyebrow"><Sparkles size={15} /> Official campus gear</p><h1>Shop<br /><em>Bulldog Blue.</em></h1><p className="lede">Casual comfort, classic Bulldog pride. Find the pieces that make campus feel like yours.</p><a className="button pink" href="#products">Shop the collection <ArrowRight size={16} /></a></div><div className="hero-mark" aria-hidden="true"><span>Y</span><small>YALE<br />EST. 1701</small></div></section><section className="marquee"><span>TOP IT OFF</span><span>•</span><span>SHOW YOUR BLUE</span><span>•</span><span>TOP IT OFF</span></section><section className="shop"><div className="section-heading"><div><p className="eyebrow">Made for every campus moment</p><h2>Popular picks</h2></div><a className="text-link" href="#products">View all products <ArrowRight size={14} /></a></div><ProductGrid query="hoodie" /></section></>
}

function Products() {
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('All')
  return <section className="shop products-page"><div className="page-intro"><p className="eyebrow">The full collection</p><h1>Find your <em>blue.</em></h1><p>From everyday layers to game-day favorites, bring a little Bulldog spirit wherever you go.</p></div><div className="search-row"><div className="search"><Search size={18} /><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search the catalogue" aria-label="Search the catalogue" /></div><label className="filter-label" htmlFor="category-filter">Category</label><select id="category-filter" className="filter" value={category} onChange={(e) => setCategory(e.target.value)}><option>All</option><option>hoodie</option><option>crewneck</option><option>T-shirt</option><option>jacket</option><option>1/4-zip</option><option>tennis</option></select></div><ProductGrid query={query} category={category} /></section>
}

function About() {
  return <section className="about-page"><div className="about-lead"><p className="eyebrow">Our story</p><h1>Campus looks<br /><em>good on you.</em></h1><p className="lede">Campus Customs is your home for everyday Yale style—clothing and accessories made for the people who make campus special.</p></div><div className="about-grid"><div><span className="about-number">01</span><h2>What we sell</h2><p>We bring together comfortable hoodies, crewnecks, T-shirts, jackets, and campus-ready accessories. Whether you are headed to class, the game, or home for the weekend, there is something here for your rotation.</p></div><div><span className="about-number">02</span><h2>Why shop with us</h2><p>We make finding your Bulldog Blue easy. Browse Yale favorites, check sizes and availability, and discover pieces that let you show your pride without giving up your personal style.</p></div></div><a className="button pink" href="#products">Explore the collection <ArrowRight size={16} /></a></section>
}

function Account({ create = false }: { create?: boolean }) {
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const submit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault(); setStatus(''); setError(''); setLoading(true)
    const form = new FormData(e.currentTarget)
    const password = String(form.get('password') || '')
    if (create && password !== String(form.get('confirm_password') || '')) { setError('Passwords do not match.'); setLoading(false); return }
    const body = create ? { first_name: form.get('first_name'), last_name: form.get('last_name'), email: form.get('email'), password } : { email: form.get('email'), password }
    try { const response = await fetch(API_BASE_URL + '/api/auth/' + (create ? 'register' : 'login'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }); const data = await response.json(); if (!response.ok) throw new Error(data.detail || 'Something went wrong.'); localStorage.setItem('campus_customs_user', JSON.stringify(data.user)); setStatus(create ? 'Account created! You can now log in.' : `Welcome back, ${data.user.first_name || data.user.name}!`) } catch (requestError) { setError(requestError instanceof Error ? requestError.message : 'Unable to reach the Campus Customs server.') } finally { setLoading(false) }
  }
  return <section className="account-page"><div className="account-card"><p className="eyebrow">Campus Customs</p><h1>{create ? 'Create your account.' : 'Welcome back.'}</h1><p>{create ? 'Save your favorites and keep your campus style close.' : 'Log in to keep shopping Bulldog Blue.'}</p><form onSubmit={submit}>{create && <input name="first_name" required placeholder="First name" />}{create && <input name="last_name" required placeholder="Last name" />}{<input name="email" required type="email" placeholder="Email address" />}{<input name="password" required minLength={8} type="password" placeholder="Password (8+ characters)" />}{create && <input name="confirm_password" required minLength={8} type="password" placeholder="Confirm password" />}<button className="button pink" type="submit" disabled={loading}>{loading ? 'Please wait...' : create ? 'Create account' : 'Log in'} <ArrowRight size={16} /></button></form>{error && <p className="form-message error">{error}</p>}{status && <p className="form-message">{status}</p>}</div></section>
}

function ChatStub({ onProducts, pageContext }: { onProducts: (products: Product[]) => void; pageContext: { route: string; product_id?: string; name?: string } }) {
  const [open, setOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [messages, setMessages] = useState([{ from: 'bot', text: 'Hi! I’m the Campus Customs assistant. How can I help you shop Bulldog Blue?' }])
  useEffect(() => {
    if (!open) return
    const storedUser = localStorage.getItem('campus_customs_user')
    if (!storedUser) return
    try {
      const user = JSON.parse(storedUser) as { id: number }
      fetch(`${API_BASE_URL}/api/chat/history/${user.id}`).then((response) => response.ok ? response.json() : []).then((history) => { if (Array.isArray(history) && history.length) setMessages(history.map((item: { role: string; content: string }) => ({ from: item.role === 'assistant' ? 'bot' : 'user', text: item.content }))) }).catch(() => undefined)
    } catch { localStorage.removeItem('campus_customs_user') }
  }, [open])
  const sendMessage = async (e: FormEvent) => {
    e.preventDefault()
    if (!message.trim()) return
    const text = message.trim()
    setMessages((current) => [...current, { from: 'user', text }])
    setMessage('')
    setSending(true)
    try {
      const storedUser = localStorage.getItem('campus_customs_user')
      const user = storedUser ? JSON.parse(storedUser) as { id: number } : null
      const response = await fetch(`${API_BASE_URL}/api/chat`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: text, user_id: user?.id ?? null, page_context: pageContext }) })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'The assistant is unavailable right now.')
      if (Array.isArray(data.products) && data.products.length > 0) { onProducts(data.products); setMessages((current) => [...current, { from: 'bot', text: `${data.reply} I’ve displayed the matching items on the Products page.` }]); window.location.hash = '#products' } else setMessages((current) => [...current, { from: 'bot', text: data.reply }])
    } catch (error) {
      setMessages((current) => [...current, { from: 'bot', text: error instanceof Error ? error.message : 'The assistant is unavailable right now.' }])
    } finally { setSending(false) }
  }
  return <div className={`chat-widget ${open ? 'is-open' : ''}`}><button className="chat-launcher" onClick={() => setOpen(!open)} aria-label={open ? 'Close chat' : 'Open chat'}>{open ? <X size={21} /> : <Bot size={21} />} {!open && <span>Chat with us</span>}</button>{open && <section className="chat-panel" aria-label="Campus Customs chat"><div className="chat-header"><div><strong>Campus Customs</strong><small>Shopping assistant</small></div><span className="online-dot" /></div><div className="chat-messages">{messages.map((item, index) => <div className={`chat-message ${item.from}`} key={`${item.from}-${index}`}>{item.text}</div>)}{sending && <div className="chat-message bot">Looking through the catalogue...</div>}</div>{messages.length === 1 && <div className="quick-prompts"><button onClick={() => setMessage('What hoodies do you have?')}>Show me hoodies</button><button onClick={() => setMessage('What is in stock?')}>What’s in stock?</button></div>}<form className="chat-form" onSubmit={sendMessage}><input value={message} onChange={(e) => setMessage(e.target.value)} placeholder="Ask about products..." aria-label="Chat message" disabled={sending} /><button type="submit" aria-label="Send message" disabled={sending}><Send size={16} /></button></form></section>}</div>
}

function App() {
  const [page, setPage] = useState(window.location.hash.replace('#', '') || 'home')
  const [agentProducts, setAgentProducts] = useState<Product[]>([])
  useEffect(() => { const update = () => setPage(window.location.hash.replace('#', '') || 'home'); window.addEventListener('hashchange', update); return () => window.removeEventListener('hashchange', update) }, [])
  const content = page.startsWith('product/') ? <ProductDetail productId={page.slice('product/'.length)} /> : page === 'products' ? <Products /> : page === 'about' ? <About /> : page === 'login' ? <Account /> : page === 'create-account' ? <Account create /> : <Home />
  const viewedProduct = page.startsWith('product/') ? catalogue.find((item) => item.product_id === page.slice('product/'.length)) : undefined
  const currentPageContext = { route: page, ...(viewedProduct ? { product_id: viewedProduct.product_id, name: viewedProduct.name } : {}) }
  return <main className="shell"><nav className="nav"><a className="brand" href="#home">CAMPUS<span>CUSTOMS</span></a><div className="nav-links"><a className={page === 'home' ? 'active' : ''} href="#home">Home</a><a className={page === 'products' ? 'active' : ''} href="#products">Products</a><a className={page === 'about' ? 'active' : ''} href="#about">About Us</a><a className={page === 'login' ? 'active' : ''} href="#login">Log in</a><a className="account-link" href="#create-account">Create account</a></div><button className="icon-button" aria-label="Shopping bag"><ShoppingBag size={20} /><span>0</span></button></nav>{content}{agentProducts.length > 0 && <section className="agent-results"><div className="section-heading"><div><p className="eyebrow">From your shop assistant</p><h2>Matching products</h2></div><button className="clear-results" onClick={() => setAgentProducts([])}>Clear results</button></div><ProductGrid items={agentProducts} /></section>}<footer><span>© 2026 Campus Customs</span><span>Made for the Yale community</span></footer><ChatStub onProducts={setAgentProducts} pageContext={currentPageContext} /></main>
}

export default App

function App() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui' }}>
      <h1>SCIMS</h1>
      <p>Star Citizen Inventory Management System</p>
      <p>Frontend is running. Backend API should be available at <code>{import.meta.env.VITE_API_URL || '/api/v1'}</code></p>
    </div>
  )
}

export default App


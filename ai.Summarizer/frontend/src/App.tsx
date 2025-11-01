import { useState } from 'react'
import { ConfigProvider, theme } from 'antd'
import Summarizer from './components/Summarizer'
import './App.css'

function App() {
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#0047AB',  // Professional blue inspired by Morgan Stanley
          borderRadius: 4,
          fontSize: 14,
        },
      }}
    >
      <div className="app">
        <Summarizer />
      </div>
    </ConfigProvider>
  )
}

export default App

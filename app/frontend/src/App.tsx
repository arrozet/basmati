import { BrowserRouter as Router } from 'react-router-dom';
import AppRouter from './presentation/router/AppRouter';
import { CalendarVisibilityProvider } from './presentation/context/CalendarVisibilityContext';

function App() {
  return (
    <Router>
      <CalendarVisibilityProvider>
        <AppRouter />
      </CalendarVisibilityProvider>
    </Router>
  )
}

export default App


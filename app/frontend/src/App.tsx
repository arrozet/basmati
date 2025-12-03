import { BrowserRouter as Router } from 'react-router-dom';
import AppRouter from './presentation/router/AppRouter';
import { CalendarVisibilityProvider } from './presentation/context/CalendarVisibilityContext';
import { User_Provider } from './presentation/context/UserContext';

function App() {
  return (
    <Router>
      <User_Provider>
        <CalendarVisibilityProvider>
          <AppRouter />
        </CalendarVisibilityProvider>
      </User_Provider>
    </Router>
  )
}

export default App


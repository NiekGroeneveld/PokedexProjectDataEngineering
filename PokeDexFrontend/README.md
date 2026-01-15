# PokeDex - Interactive Pokemon Encyclopedia

A modern, interactive Pokemon encyclopedia built with React, TypeScript, and Vite. This application allows users to search, view, and explore Pokemon data with a clean, type-themed interface.

## 🚀 Features

### ✅ Current Functionalities

#### 1. **Global Pokemon State Management**
- Centralized Pokemon context using React Context API
- `usePokemon` hook accessible throughout the application
- Maintains selected Pokemon state across all components

#### 2. **Pokemon Search**
- Real-time search functionality in the navigation bar
- Dropdown suggestions showing Pokemon details:
  - Pokemon ID (formatted as #001, #025, etc.)
  - Pokemon name
  - Type badges with color-coded backgrounds
- Click to select and view Pokemon details

#### 3. **Pokemon Database**
- Centralized database architecture in `src/data/PokemonDatabase.ts`
- Query functions for easy data access:
  - `getAllPokemon()` - Retrieve all Pokemon
  - `searchPokemonById(id)` - Find Pokemon by ID
  - `searchPokemonByName(name)` - Search by name (case-insensitive)
  - `searchPokemonByType(type)` - Filter by type
  - `getPokemonByEvolutionChain(chainIds)` - Get evolution chain members
- Currently includes: Pichu, Pikachu, and Raichu

#### 4. **Dynamic Type System**
- Type-specific color theming
- `TypeCard` component with automatic color mapping
- Supports both regular and small variants
- Currently implemented: Electric type (expandable)

#### 5. **Pokemon Display Page**
- **Top Info Bar**: Displays Pokemon ID, name, and type badges
- **Evolution Chain**: Shows Pokemon evolution stages
  - Dynamic labels based on position (Previous/Current/Next, First/Previous/Current, Current/Next/Last)
  - Type-themed card backgrounds
  - Automatic evolution chain mapping
- All components update automatically when a new Pokemon is selected

#### 6. **Component Architecture**
- Modular component structure
- Separation of concerns (UI, data, context)
- Reusable components (TypeCard, EvolutionCard, SearchBar)

## 📁 Project Structure

```
src/
├── components/
│   ├── NavBar/
│   │   ├── Navbar.tsx/css         # Main navigation with logo
│   │   └── SearchBar/             # Search functionality
│   │       ├── SearchBar.tsx/css
│   ├── PokemonPage/
│   │   ├── TopInfoBar/            # ID, name, types display
│   │   ├── EvolutionChain/        # Evolution display
│   │   │   └── EvolutionCard/     # Individual evolution cards
│   │   └── ContentSection/        # Pokemon details (in progress)
│   └── Shared/
│       └── TypeCard/              # Reusable type badge
├── contexts/
│   └── PokemonContext.tsx         # Global Pokemon state
├── data/
│   └── PokemonDatabase.ts         # Centralized Pokemon data
├── Types/
│   ├── Pokemon.ts                 # Pokemon class definition
│   └── PokemonType.ts             # Type enum and color mapping
└── assets/                        # Pokemon images

```

## 🛠️ Technologies Used

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **CSS3** - Styling with CSS variables
- **React Context API** - State management

## 🎯 Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://git.science.uu.nl/knowledgeanddataengineering/projectpokedex.git
cd projectpokedex
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

4. Open your browser to `http://localhost:5173`

### Build for Production

```bash
npm run build
```

## 🎨 Key Components

### PokemonContext
Provides global access to the selected Pokemon throughout the app.

```typescript
const { selectedPokemon, setSelectedPokemon } = usePokemon();
```

### SearchBar
Filterable search dropdown that allows users to find and select Pokemon by name.

### EvolutionChain
Dynamically displays Pokemon evolution stages based on the selected Pokemon's position in its evolution chain.

### TypeCard
Reusable component for displaying Pokemon types with automatic color theming.

## 📊 Data Model

### Pokemon Class
```typescript
class Pokemon {
  id: number
  name: string
  types: PokemonType[]
  imageUrl: string
  height: number
  weight: number
  abilities: string[]
  category: string
  evolutionChain: number[]
  stats: PokemonStats
}
```

## 🔮 Future Enhancements

- [ ] Add more Pokemon to the database
- [ ] Implement Pokemon stats visualization
- [ ] Add Pokemon abilities details
- [ ] Implement Pokemon comparison feature
- [ ] Add filtering by type, generation
- [ ] Implement favorites/bookmarks
- [ ] Add animations and transitions
- [ ] Responsive design improvements
- [ ] API integration for dynamic data

## 👨‍💻 Development

This project follows modern React best practices:
- Functional components with hooks
- TypeScript for type safety
- Component composition and reusability
- CSS variables for theming
- Modular architecture

## 📝 License

[Add your license here]

## 🙏 Acknowledgments

- Pokemon images from local assets
- Type colors based on official Pokemon types
- Built as part of Knowledge and Data Engineering course

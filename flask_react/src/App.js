import logo from './logo.svg';
import './App.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Dashboard from './Dashboard'
import SearchRecipes from './SearchRecipes'
import AddRecipes from './AddRecipes'
import SavedRecipes from './SavedRecipes'
import SuggestedRecipes from './SuggestedRecipes'

import Preferences from './Preferences'


import React from 'react';
import {
  StyleSheet,
  Button,
  View,
  SafeAreaView,
  Text,
  Alert,
} from 'react-native';

import {NavigationContainer} from '@react-navigation/native';
import {createNativeStackNavigator} from '@react-navigation/native-stack';

function Page() {
  return (
    <div className="wrapper">
      <h1>Application</h1>
      <BrowserRouter>
        <Routes>
          <Route path="/dashboard">
            <Dashboard />
          </Route>
          <Route path="/preferences">
            <Preferences />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

const Stack = createNativeStackNavigator();

const App = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator>
        <Stack.Screen
          name="Home"
          component={HomeScreen}
          options={{title: 'Welcome'}}
        />
        <Stack.Screen name="Profile" component={ProfileScreen} />
        <Stack.Screen name="Dashboard" component={Dashboard} />
        <Stack.Screen name="Search Recipes" component={SearchRecipes} />
        <Stack.Screen name="Add Recipes" component={AddRecipes} />
        <Stack.Screen name="Saved Recipes" component={SavedRecipes} />
        <Stack.Screen name="Suggested Recipes" component={SuggestedRecipes} />

      </Stack.Navigator>
    </NavigationContainer>
  );
};

const HomeScreen = ({navigation}) => {
  return (
    <div className="App">
      <header className="App-header">

        <img src={logo} className="App-logo" alt="logo" />

        <p>
          Food Your Way
        </p>

    <View style={[{ width: "40%", margin: 20 }]}>
		<Button
  		onPress={() => navigation.navigate('Dashboard', {name: 'TEMP_USERNAME'})}
  		title="Dashboard"
  		color="#50afff"
  		accessibilityLabel="Dashboard"/>
	</View>

	<View style={[{ width: "40%", margin: 20 }]}>
		<Button
  		onPress={() => navigation.navigate('Search Recipes', {name: 'TEMP_USERNAME'})}
  		title="Search Recipes"
  		color="#50afff"
  		accessibilityLabel="Search for recipes"/>
	</View> 

	<View style={[{ width: "40%", margin: 20 }]}>
		<Button
  		onPress={() => navigation.navigate('Add Recipes', {name: 'TEMP_USERNAME'})}
  		title="Add Recipes"
  		color="#50afff"
  		accessibilityLabel="Add new recipes"/>
	</View>

    <View style={[{ width: "40%", margin: 20 }]}>
		<Button
  		onPress={() => navigation.navigate('Saved Recipes', {name: 'TEMP_USERNAME'})}
  		title="Saved Recipes"
  		color="#50afff"
  		accessibilityLabel="Saved Recipes"/>
	</View>

	<View style={[{ width: "40%", margin: 20 }]}>
		<Button
  		onPress={() => navigation.navigate('Suggested Recipes', {name: 'TEMP_USERNAME'})}
  		title="Suggested Recipes"
  		color="#50afff"
  		accessibilityLabel="Suggested recipes based on search"/>
	</View>

      </header>
    </div>
  );
};

const ProfileScreen = ({navigation, route}) => {
  return <Text>This is {route.params.name}'s profile</Text>;
};

const DashboardScreen = ({navigation, route}) => {
  return <Text> Dashboard screen! {route.params.name}'s profile</Text>;
};

export default App;

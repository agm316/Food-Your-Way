import React from 'react';
import {
  StyleSheet,
  Button,
  View,
  SafeAreaView,
  Text,
  Alert,
} from 'react-native';

const SuggestedRecipes = ({navigation, route}) => {
  return <Text> Suggested recipes screen! {route.params.name}'s profile</Text>;
};

export default SuggestedRecipes;
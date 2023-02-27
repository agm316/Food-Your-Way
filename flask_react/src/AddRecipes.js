import React from 'react';
import {
  StyleSheet,
  Button,
  View,
  SafeAreaView,
  Text,
  Alert,
} from 'react-native';

const AddRecipes = ({navigation, route}) => {
  return <Text> Add new recipes screen! {route.params.name}'s profile</Text>;
};

export default AddRecipes;
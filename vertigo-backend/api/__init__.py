"""
Welcome to the documentation for Vertigo, the ultimate web app for managing your comic book collection!

Vertigo is a modern and responsive web application built to streamline the organization and tracking of your physical comic book collection. Crafted with Vue.js and Flask, Vertigo offers a seamless user experience with powerful features to enhance your comic book management.

## Introduction

Vertigo is designed with the following goals in mind:

- **Track and Curate Collection**: Easily organize and manage your comic book collection, ensuring that every issue is accounted for and easily accessible.

- **Search and Filter**: Utilize intuitive search and filter options based on various criteria such as title, publisher, and more. Find specific issues or explore your collection effortlessly.

- **Reading Progress Tracking**: Keep tabs on your reading progress with features to mark issues as read or unread, manage backlogs, and even assign ratings for your favorite comics.

- **Insightful Statistics**: Gain valuable insights into your collection with detailed statistics. Understand trends, favorite series, and more to optimize your comic book experience.

- **Integration with External APIs**: Explore options to seamlessly integrate with external APIs for automatic fetching of details. Enhance your collection with up-to-date information and cover images.

- **Backup and Export**: Ensure the safety of your data with backup and export functionalities. Export your collection data to commonly used formats for peace of mind.

## Get Started

Vertigo is your companion for organizing and enjoying your comic book collection like never before. Whether you're a casual reader or a die-hard collector, Vertigo offers the tools and features to elevate your comic book experience.

Feel free to reach out if you have any questions or suggestions. We're here to help you make the most out of Vertigo!

Happy collecting!

"""  # noqa: E501

from api.app import create_app, db, ma  # noqa: F401

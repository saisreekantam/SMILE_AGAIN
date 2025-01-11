import React,{ useEffect } from 'react'
import LandingPage from './LandingPage';
import { Routes,Route } from 'react-router-dom';
import LoginPage from './LoginPage';
import RegistrationPage from './RegistrationPage';
import ProblemDescriptionForm from './ProblemDescriptionForm';
import ChatBotPage from './ChatBotPage';
import ProfilePage from './ProfilePage';
import ViewFriends from './FriendsPage';
import CommentsPage from './CommentsPage';
import BlogsPage from './BlogsPage';
import ChatsPage from './ChatsPage';
import GroupChatPage from './GroupChat';
import GroupPage from './GroupPage';
import AddBlog from './AddBlog';
import WorkshopsList from './WorkshopsList';
import AddWorkshop from './AddWorkShop';
import FeedbacksPage from './WorkshopFeedbacks';
import UserProfileView from './AuthorProfilePage';
import FriendRequestsPage from './NotificationsPage';
import PostPage from './PostsPage';
import MoodTrackerPage from './MoodDescription';
import ChatPage from './FriendChatPage';
import EnhancedActivityDashboard from './ActivitiesPage';
import BlogDetailsPage from './BlogDetailsPage';
import MeditationTimer from './MeditationTimer';
import JourneyDashboard from './SmileJourneyPage';
import GroupGamesPage from './GroupGames';
import CommunityActivities from './CommunitiesAI';

function App() {
  return (
    <>
      <Routes>
        <Route path='/' element={<LandingPage />} />
        <Route path='/friends' element={<ViewFriends />} />
        <Route path='/login' element={<LoginPage />} />
        <Route path='/register' element={<RegistrationPage />} />
        <Route path='/problem_page' element={<ProblemDescriptionForm />} />
        <Route path='/chats' element={<ChatsPage />} />
        <Route path='/home' element={<ChatBotPage />} />
        <Route path='/myProfile' element={<ProfilePage />} />
        <Route path='/blogs' element={<BlogsPage />} />
        <Route path='/blogs/:blogId' element={<BlogDetailsPage />} />
        <Route path='/blogs/:blogId/comments' element={<CommentsPage />} />
        <Route path='/groups' element={<GroupChatPage />} />
        <Route path='/groups/:groupId' element={<GroupPage />} />
        <Route path='/add-blog' element={<AddBlog />} />
        <Route path='/workshops' element={<WorkshopsList />} />
        <Route path='/workshops/create' element={<AddWorkshop />} />
        <Route path="/workshops/:workshopId/feedback" element={<FeedbacksPage />} />
        <Route path='/user/:userId' element={<UserProfileView />} />
        <Route path='/notifications' element={<FriendRequestsPage />} />
        <Route path='/community/:postId' element={<PostPage />} />
        <Route path='/mood_entry' element={<MoodTrackerPage />} />
        <Route path='/friends/:friendId' element={<ChatPage />} />
        <Route path='/activities' element={<EnhancedActivityDashboard />} />
        <Route path='/meditation_timer' element={<MeditationTimer />} />
        {/* <Route path='/your_smile_journey/:community_id' element={<JourneyDashboard />} />
        <Route path='/group_games/:groupId' element={<GroupGamesPage />} /> */}
        <Route path='/my_journey' element={<CommunityActivities />} />
      </Routes>
    </>
  );
}

export default App;


import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getDocuments, getConversations } from '../api/client';
import { Document, Conversation } from '../types';
import { toast } from 'react-toastify';

const Dashboard: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [documentsResponse, conversationsResponse] = await Promise.all([
          getDocuments(),
          getConversations(),
        ]);
        setDocuments(documentsResponse);
        setConversations(conversationsResponse);
      } catch (err) {
        setError('Failed to fetch data. Please try again.');
        toast.error('Error fetching dashboard data.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleUploadClick = () => {
    navigate('/upload');
  };

  const handleChatClick = () => {
    navigate('/chat');
  };

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      {loading ? (
        <div className="text-center text-gray-500">Loading...</div>
      ) : error ? (
        <div className="text-center text-red-500">{error}</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white shadow rounded-lg p-4">
              <h2 className="text-lg font-semibold">Documents</h2>
              <p className="text-2xl font-bold">{documents.length}</p>
            </div>
            <div className="bg-white shadow rounded-lg p-4">
              <h2 className="text-lg font-semibold">Conversations</h2>
              <p className="text-2xl font-bold">{conversations.length}</p>
            </div>
          </div>
          <div className="mb-6">
            <h2 className="text-xl font-bold mb-4">Recent Documents</h2>
            <div className="bg-white shadow rounded-lg p-4">
              {documents.length === 0 ? (
                <p className="text-gray-500">No documents available.</p>
              ) : (
                <ul className="divide-y divide-gray-200">
                  {documents.slice(0, 5).map((doc) => (
                    <li key={doc.id} className="py-2">
                      {doc.name}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
          <div className="mb-6">
            <h2 className="text-xl font-bold mb-4">Recent Conversations</h2>
            <div className="bg-white shadow rounded-lg p-4">
              {conversations.length === 0 ? (
                <p className="text-gray-500">No conversations available.</p>
              ) : (
                <ul className="divide-y divide-gray-200">
                  {conversations.slice(0, 5).map((conv) => (
                    <li key={conv.id} className="py-2">
                      {conv.title || 'Untitled Conversation'}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
          <div className="flex gap-4">
            <button
              onClick={handleUploadClick}
              className="bg-blue-500 text-white px-4 py-2 rounded shadow hover:bg-blue-600"
            >
              Upload Document
            </button>
            <button
              onClick={handleChatClick}
              className="bg-green-500 text-white px-4 py-2 rounded shadow hover:bg-green-600"
            >
              Start Chat
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;